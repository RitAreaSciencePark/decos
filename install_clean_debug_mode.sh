#!/bin/bash
set -euo pipefail

ENV_SETUP=".env.dev.setup"
ENV_DEV=".env.dev"

SECRETS_DIR=".secrets"
SECRETS_BUNDLE="$SECRETS_DIR/bundle.env"
SECRETS_RUNTIME_DIR="$SECRETS_DIR/.runtime"

mkdir -p "$SECRETS_DIR" "$SECRETS_RUNTIME_DIR"
chmod 700 "$SECRETS_DIR" "$SECRETS_RUNTIME_DIR" 2>/dev/null || true


## -- NOT USED (for now)

b64enc() { printf '%s' "$1" | base64 | tr -d '\n'; }
b64dec() { printf '%s' "$1" | base64 -d; }

# write or update KEY_B64=... in bundle.env
bundle_set() {
  local key="$1" val="$2" b64
  b64="$(b64enc "$val")"
  touch "$SECRETS_BUNDLE"
  grep -v -E "^${key}_B64=" "$SECRETS_BUNDLE" > "$SECRETS_BUNDLE.tmp" || true
  printf '%s_B64=%s\n' "$key" "$b64" >> "$SECRETS_BUNDLE.tmp"
  mv "$SECRETS_BUNDLE.tmp" "$SECRETS_BUNDLE"
  chmod 600 "$SECRETS_BUNDLE" || true
}

# read KEY_B64=… and decode
bundle_get() {
  local key="$1" b64
  b64="$(grep -E "^${key}_B64=" "$SECRETS_BUNDLE" | head -n1 | cut -d= -f2- || true)"
  [ -n "$b64" ] && b64dec "$b64"
}

# materialize a plain-text secret file from bundle to .runtime and export both *_HOST_FILE and value
materialize_secret() {
  local key="$1" fname="$SECRETS_RUNTIME_DIR/${key,,}.txt"
  local val
  val="$(bundle_get "$key")"
  [ -z "$val" ] && return 0
  printf '%s' "$val" > "$fname"
  chmod 600 "$fname" || true
  export "${key}_HOST_FILE=$fname"
  export "$key=$val"
}
## -- END NOT USED (for now)



for arg in "$@"; do
  case "$arg" in
      # --> args handle --rmall flag, remove containers and volumes
      "--rmall")
      echo "🧹  --rmall specified: stopping containers and removing images + volumes"

      # Safety: ensure compose files exist
      COMPOSE_ENV_FILE="${COMPOSE_ENV_FILE:-.env.dev}"
      COMPOSE_FILE="${COMPOSE_FILE:-docker-compose-dev.yaml}"

      if [[ ! -f "$COMPOSE_ENV_FILE" ]]; then
        echo "⚠️  Env file not found: $COMPOSE_ENV_FILE"
      fi
      if [[ ! -f "$COMPOSE_FILE" ]]; then
        echo "⚠️  Compose file not found: $COMPOSE_FILE"
      fi

      # Bring the stack down, remove images and volumes
      docker compose --env-file "$COMPOSE_ENV_FILE" -f "$COMPOSE_FILE" down --rmi all --volumes || \
        echo "ℹ️  'docker compose down' returned non-zero (stack may not be running)."

      # Optionally remove the named container if it exists
      if [[ -n "${WEBAPP_CONTAINER:-}" ]] && docker ps -a --format '{{.Names}}' | grep -qx "$WEBAPP_CONTAINER"; then
        echo "🛑  Removing container: $WEBAPP_CONTAINER"
        docker rm -f "$WEBAPP_CONTAINER" || echo "⚠️  Failed to remove $WEBAPP_CONTAINER"
      else
        echo "ℹ️  \$WEBAPP_CONTAINER not set or container not found."
      fi

      # Networks created by Compose are removed by 'down' automatically (unless external)
      echo "✅  Completed --rmall."
    ;;
    # --> args handle --reinit flag, rewrite env.dev 
    "--reinit")
      if [ -f "$ENV_DEV" ]; then
        echo "♻️  --reinit specified: removing $ENV_DEV"
        cp "$ENV_DEV" "$ENV_DEV.bak"
        rm -f "$ENV_DEV"
      else
        echo "♻️  --reinit specified: nothing to remove ($ENV_DEV not found)"
      fi
    ;;
  esac
done

# ---- helpers ----
# BEWARE: dependent on openssl
# Generate automatically a strong password (usually with !generate)
gen_secret() {
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -base64 32 | tr -d '\n'
  else
    head -c 32 /dev/urandom | base64 | tr -d '\n' || echo "changeme-$(date +%s)"
  fi
}

# Ask to insert a value, e.g., localhost or if a single return put the default value
prompt_var() {
  local key="$1" default="$2" value=""
  if [ -n "$default" ]; then
    >&2 printf "%s [%s]: " "$key" "$default"
  else
    >&2 printf "%s: " "$key"
  fi
  IFS= read -r value < /dev/tty || true
  [ -z "$value" ] && value="$default"
  printf "%s" "$value"
}

# Same thing, but with secrets
prompt_secret() {
  local key="$1" default="$2" value="" confirm=""
  >&2 echo "Tip: ENTER for default, or type !generate to auto-generate."
  while true; do
    >&2 printf "%s [hidden]: " "$key"
    IFS= read -r -s value < /dev/tty || true
    >&2 echo
    [ -z "$value" ] && value="$default"

    # uses !generate to create a new value, do not ask again for it
    if [ "$value" = "!generate" ]; then
      value="$(gen_secret)"
      >&2 echo "  → generated"
      printf "%s" "$value"
      return 0   # ✅ skip confirmation
    fi

    >&2 printf "Confirm %s: " "$key"
    IFS= read -r -s confirm < /dev/tty || true
    >&2 echo
    if [ "$confirm" = "$value" ]; then
      printf "%s" "$value"
      return 0
    fi
    >&2 echo "❌ Values do not match, try again."
  done
}

# ---- end helpers ----

echo "🔐 Preparing .env.dev…"

HOST_VALUE=""  # will cache the replacement for 'localhost'

if [ -f "$ENV_DEV" ]; then
  echo "ℹ️ $ENV_DEV already exists. Skipping interactive creation."
else
  echo "🧰 Creating $ENV_DEV from $ENV_SETUP (interactive)…"
  echo "# Generated on $(date)" > "$ENV_DEV"

  while IFS= read -r line; do
    # skip blanks/comments and malformed lines
    [ -z "$line" ] && continue
    case "$line" in \#*) continue ;; esac
    [[ "$line" != *"="* ]] && continue

    key="${line%%=*}"
    default="${line#*=}"

    if [[ "$default" == "changeme" ]] || [[ "$default" == *"localhost"* ]]; then
      case "$key" in
        # treat secrets the same as you already do
        *PASSWORD*|*SECRET*|*TOKEN*|*KEY*)
          value="$(prompt_secret "$key" "$default")"

          file_base="$(printf '%s' "$key" | tr '[:upper:]' '[:lower:]' | tr -c 'a-z0-9_' '_')"
          host_secret_path="$SECRETS_DIR/${file_base}.txt"
          printf '%s' "$value" > "$host_secret_path"
          chmod 600 "$host_secret_path" 2>/dev/null || true

          printf "%s_HOST_FILE=%s\n" "$key" "$host_secret_path" >> "$ENV_DEV"
          export "${key}_HOST_FILE=$host_secret_path"
          export "$key=$value"
          continue
          ;;

        # SPECIAL HOST-FORMATTED KEYS
        WAGTAIL_HOSTNAME|SERVER_NAME|DECOS_ALLOWED_HOSTS)
          if [[ -z "$HOST_VALUE" ]]; then
            HOST_VALUE="$(prompt_var "HOST (replace 'localhost' everywhere)" "localhost")"
          fi
          value="${HOST_VALUE}"
          ;;

        WAGTAILADMIN_BASE_URL)
          if [[ -z "$HOST_VALUE" ]]; then
            HOST_VALUE="$(prompt_var "HOST (replace 'localhost' everywhere)" "localhost")"
          fi
          value="http://${HOST_VALUE}"
          ;;

        CSRF_TRUSTED_ORIGINS)
          if [[ -z "$HOST_VALUE" ]]; then
            HOST_VALUE="$(prompt_var "HOST (replace 'localhost' everywhere)" "localhost")"
          fi
          value="[http://${HOST_VALUE}, https://${HOST_VALUE}']"
          ;;

        *)
          # Generic handling:
          # - If default mentions localhost, replace it with cached HOST_VALUE (ask once)
          # - Else if it's 'changeme', prompt normally
          if [[ "$default" == *"localhost"* ]]; then
            if [[ -z "$HOST_VALUE" ]]; then
              HOST_VALUE="$(prompt_var "HOST (replace 'localhost' everywhere)" "localhost")"
            fi
            value="${default//localhost/${HOST_VALUE}}"
          else
            value="$(prompt_var "$key" "$default")"
          fi
          ;;
      esac
    else
      value="$default"
    fi

    printf "%s=%s\n" "$key" "$value" >> "$ENV_DEV"
  done < "$ENV_SETUP"
  echo "✅ Wrote $ENV_DEV"
fi



echo "✅ .env.dev ready."

# Load only the keys the script needs, from .env.dev (no process substitution)
if [ -f "$ENV_DEV" ]; then
  while IFS= read -r line; do
    # strip trailing CR (Windows line endings)
    line=${line%$'\r'}

    # skip blanks and comments
    [ -z "$line" ] && continue
    case "$line" in \#*) continue ;; esac
    case "$line" in
      *PASSWORD_HOST_FILE=*|*SECRET_HOST_FILE=*|*TOKEN_HOST_FILE=*|*KEY_HOST_FILE=*)
        k="${line%%_HOST_FILE=*}"
        f="${line#*=}"
        export "${k}_HOST_FILE=$f"
        if [ -f "$f" ]; then
          export "$k=$(cat "$f")"
        else
          # ensure .secrets/ directory exists
          mkdir -p "$(dirname "$f")"
          : > "$f"   # create empty file
          echo "⚠️  Secret file not found for $k: $f → created empty one" >&2
        fi
        ;;
      DB_CONTAINER=*|WEBAPP_CONTAINER=*|DJANGO_DIR=*|POSTGRES_DB=*|POSTGRES_USER=*|POSTGRES_PASSWORD=*|POSTGRES_VOLUME=*|WEB_APP_PORT=*|DEBUGPY_PORT=*|SUPERUSER_NAME=*|SUPERUSER_PASSWORD=*|SUPERUSER_EMAIL=*)
        k=${line%%=*}; v=${line#*=}; export "$k=$v"
        ;;
      *) : ;;
    esac


  done < "$ENV_DEV"
fi


# Set environment variables
echo "🚀 Rebuilding and starting fresh containers..."
docker compose --env-file .env.dev -f docker-compose-dev.yaml up -d --build

echo "⌛ Waiting for PostgreSQL to be ready..."
until docker exec "$DB_CONTAINER" pg_isready -U $POSTGRES_USER; do
    sleep 2
done
echo "✅ PostgreSQL is ready!"

echo "⌛ Waiting for the Django webapp container to be ready..."
until docker logs "$WEBAPP_CONTAINER" 2>&1 | grep -q "Note: Debugging will proceed"; do
    sleep 2
done
echo "✅ Django webapp is ready!"

echo "🚀 Applying Django migrations..."
docker exec -w "$DJANGO_DIR" "$WEBAPP_CONTAINER" python3 manage.py migrate --verbosity=0
docker exec -w "$DJANGO_DIR" "$WEBAPP_CONTAINER" python3 manage.py migrate --database=prpmetadata-db --verbosity=0
echo "✅ Migrations applied successfully!"

# Run the separate Wagtail setup script
./setup_wagtail.sh
echo "✅ Digital ECOSystem database init completed!"


echo "🚀 Restarting webapp to ensure all changes take effect..."
docker restart "$WEBAPP_CONTAINER"

echo "✅ DECOS Django Wagtail setup complete! 🎉"
echo "🧠 remember to attach debugpy to start the server!"
