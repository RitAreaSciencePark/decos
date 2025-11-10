#!/usr/bin/env bash
# apply_migrations.sh
# Usage: ./apply_migrations.sh [path/to/.env.dev]
# Loads only DJANGO_DIR and WEBAPP_CONTAINER from the env file

set -euo pipefail

ENV_FILE="${1:-.env.dev}"

# Read a single KEY=VALUE from an env file (no process substitution)
read_env_var() {
  local key="$1" file="$2" line val
  line="$(grep -E "^[[:space:]]*${key}=" "$file" | tail -n1 || true)"
  [ -n "$line" ] || return 1
  val="${line#*=}"
  val="${val%$'\r'}"
  case "$val" in
    \"*\") val="${val%\"}"; val="${val#\"}";;
    \'*\') val="${val%\'}"; val="${val#\'}";;
  esac
  printf '%s' "$val"
}

# Ensure env file exists
[ -f "$ENV_FILE" ] || { echo "❌ Env file not found: $ENV_FILE" >&2; exit 1; }

# Load only the two needed vars from env file
DJANGO_DIR="$(read_env_var DJANGO_DIR "$ENV_FILE" || true)"
WEBAPP_CONTAINER="$(read_env_var WEBAPP_CONTAINER "$ENV_FILE" || true)"

[ -n "${DJANGO_DIR:-}" ] || { echo "❌ Missing DJANGO_DIR in $ENV_FILE" >&2; exit 1; }
[ -n "${WEBAPP_CONTAINER:-}" ] || { echo "❌ Missing WEBAPP_CONTAINER in $ENV_FILE" >&2; exit 1; }

echo "🧩 Using DJANGO_DIR=$DJANGO_DIR"
echo "🧩 Using WEBAPP_CONTAINER=$WEBAPP_CONTAINER"

# Optional: quick check the container is up
if ! docker ps --format '{{.Names}}' | grep -qx "$WEBAPP_CONTAINER"; then
  echo "❌ Container '$WEBAPP_CONTAINER' is not running." >&2
  exit 1
fi

echo "🛠️  Making migrations..."
docker exec -w "$DJANGO_DIR" "$WEBAPP_CONTAINER" python3 manage.py makemigrations --noinput --verbosity=0

echo "🚀 Applying Django migrations..."

echo "⚠️  Faking migration auth.0013_group_laboratory..."

# This is faked as we used User group as lab groups, so they are the same relation
docker exec -w "$DJANGO_DIR" "$WEBAPP_CONTAINER" \
  python3 manage.py migrate auth 0013_group_laboratory --fake --noinput --verbosity=0

docker exec -w "$DJANGO_DIR" "$WEBAPP_CONTAINER" python3 manage.py migrate --noinput --verbosity=0
docker exec -w "$DJANGO_DIR" "$WEBAPP_CONTAINER" python3 manage.py migrate --database=prpmetadata-db --noinput --verbosity=0


echo "♻️  Restarting container s'$WEBAPP_CONTAINER'..."
docker restart "$WEBAPP_CONTAINER" >/dev/null

echo "✅ Migrations applied (with auth.0013_group_laboratory faked) and container restarted successfully!"




