#!/bin/bash
set -euo pipefail

ENV_SETUP=".env.dev.setup"
ENV_DEV=".env.dev"


for arg in "$@"; do
  case "$arg" in
      # --> args handle --rmall flag, remove containers and volumes
      "--rmall")
      echo "🧹  --rmall specified: stopping containers and removing images + volumes"

      # Safety: ensure compose files exist
      COMPOSE_ENV_FILE="${COMPOSE_ENV_FILE:-.env.dev}"
      COMPOSE_FILE="${COMPOSE_FILE:-docker-compose-dev.yaml}"
      ls .env.dev

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

    # Decide if we should prompt or just copy
    if [[ "$default" == "changeme" ]] || [[ "$default" == *"localhost"* ]]; then
      case "$key" in
        *PASSWORD*|*SECRET*|*TOKEN*|*KEY*)
          value="$(prompt_secret "$key" "$default")"
          ;;
        *)
          value="$(prompt_var "$key" "$default")"
          ;;
      esac
    else
      value="$default"
    fi
    printf "%s=%s\n" "$key" "$value"
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

    # we only care about these keys
    case "$line" in
      DB_CONTAINER=*|WEBAPP_CONTAINER=*|DJANGO_DIR=*|POSTGRES_DB=*|POSTGRES_USER=*|POSTGRES_PASSWORD=*|POSTGRES_VOLUME=*|WEB_APP_PORT=*|DEBUGPY_PORT=*|SUPERUSER_NAME=*|SUPERUSER_PASSWORD=*|SUPERUSER_EMAIL=*)
        k=${line%%=*}
        v=${line#*=}
        export "$k=$v"
        ;;
      *) : ;;  # ignore others
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

echo "🚀 Restarting webapp to ensure all changes take effect..."
docker restart "$WEBAPP_CONTAINER"

echo "✅ DECOS Django Wagtail setup complete! 🎉"
echo "🧠 remember to attach debugpy to start the server!"
