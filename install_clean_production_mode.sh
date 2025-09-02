#!/bin/bash

# Set environment variables
DB_CONTAINER="decos_db"
WEBAPP_CONTAINER="decos_webapp"
DJANGO_DIR="/app/decos/decos_webapp"

source ./production_setup

echo "🛡️ Creating secrets_minIO.py file..."

SECRETS_PATH="decos/decos_webapp/decos_webapp/settings"
SECRETS_FILE="$SECRETS_PATH/secrets_minIO.py"

mkdir -p "$SECRETS_PATH"

cat > "$SECRETS_FILE" << EOF
class SECRETS_MINIO:
    client_id = "Hhx9cVfd39MTiQepD0qQGe30czO2hsmnwMkF2Uah"
    secret_token = "tYFhFUmTFQmlT2CuqXwcK4EfcvsJHE9rbkjVR8tMJ2W02EORfeGHtrfs5unw8QMRdUTiDu2yEm2dhbL0aew2uY2s3IWE9OhNuuH7bnrQRgZBnG0VKSnPzeATo90C9Bmy"
EOF

echo "✅ secrets_minIO.py created at $SECRETS_FILE"

echo "🚀 Stopping and removing existing containers..."
docker compose -f docker-compose-production.yaml down -v

echo "🚀 Rebuilding and starting fresh containers..."
docker compose -f docker-compose-production.yaml up -d --build

echo "⌛ Waiting for PostgreSQL to be ready..."
until docker exec "$DB_CONTAINER" pg_isready -U decos; do
    sleep 2
done
echo "✅ PostgreSQL is ready!"

echo "⌛ Waiting for the Django webapp container to be ready..."
until docker logs "$WEBAPP_CONTAINER" 2>&1 | grep -q "Booting worker with pid"; do
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
