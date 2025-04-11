#!/bin/bash

# Set environment variables
DB_CONTAINER="decos_db"
WEBAPP_CONTAINER="decos_webapp"
DJANGO_DIR="/app/django/decos_webapp"

echo "🚀 Stopping and removing existing containers..."
docker compose down -v

echo "🚀 Rebuilding and starting fresh containers..."
docker compose up -d --build

echo "⌛ Waiting for PostgreSQL to be ready..."
until docker exec "$DB_CONTAINER" pg_isready -U decos; do
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

echo "🛡️ Creating secrets_minIO.py file..."

SECRETS_PATH="django/decos_webapp/decos_webapp/settings"
SECRETS_FILE="$SECRETS_PATH/secrets_minIO.py"

mkdir -p "$SECRETS_PATH"

cat > "$SECRETS_FILE" << EOF
class SECRETS_MINIO:
    client_id = "[INSERT CLIENT ID HERE]"
    secret_token = "[INSERT SECRET TOKEN HERE]"
EOF

echo "✅ secrets_minIO.py created at $SECRETS_FILE"

# Run the separate Wagtail setup script
./setup_wagtail.sh

echo "🚀 Restarting webapp to ensure all changes take effect..."
docker restart "$WEBAPP_CONTAINER"

echo "✅ DECOS Django Wagtail setup complete! 🎉"
echo "🧠 remember to attach debugpy to start the server!"
