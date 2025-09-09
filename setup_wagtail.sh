#!/bin/bash

# Prompt for hostname input
read -p "Enter the hostname for Wagtail (e.g., decos.localhost): " WAGTAIL_HOSTNAME
# Write the hostname into production.py
# SETTINGS_FILE="/app/django/decos_webapp/decos_webapp/settings/production.py"
# docker exec -i "$WEBAPP_CONTAINER" /bin/sh -c "echo 'WAGTAILADMIN_BASE_URL = \"http://$WAGTAIL_HOSTNAME:8080\"' >> $SETTINGS_FILE"


# Feed the Python script directly to the container's Python shell
docker exec -w "$DJANGO_DIR" -i "$WEBAPP_CONTAINER" python3 manage.py shell --interface=python < ./setup_wagtail.py

echo "✅ D.ECOS. production ready setup completed!"
