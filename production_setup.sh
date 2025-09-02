#!/bin/bash

# === Step 1: Read decos.conf ===
DECOS_CONF="decos.conf"
if [ ! -f "$DECOS_CONF" ]; then
    echo "Error: $DECOS_CONF not found"
    exit 1
fi

# === Step 2: Extract variables ===
WAGTAILADMIN_BASE_URL=$(grep "^WAGTAILADMIN_BASE_URL" "$DECOS_CONF" | cut -d '=' -f2 | tr -d ' "')
RAW_ALLOWED_HOSTS=$(grep "^ALLOWED_HOSTS" "$DECOS_CONF" | cut -d '=' -f2- | tr -d "[]' ")

if [ -z "$WAGTAILADMIN_BASE_URL" ]; then
    echo "Error: WAGTAILADMIN_BASE_URL not found in $DECOS_CONF"
    exit 1
fi

if [ -z "$RAW_ALLOWED_HOSTS" ]; then
    echo "Error: ALLOWED_HOSTS not found in $DECOS_CONF"
    exit 1
fi

# === Step 3: Generate SECRET_KEY ===
DECOS_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')

# === Step 4: Generate CSRF_TRUSTED_ORIGINS ===
CSRF_TRUSTED_ORIGINS=$(echo "$RAW_ALLOWED_HOSTS" | tr ',' '\n' | sed 's/^/https:\/\//' | paste -sd, -)
CSRF_TRUSTED_ORIGINS="['${CSRF_TRUSTED_ORIGINS//,/','}']"

# === Step 5: Export environment variables ===
export WAGTAILADMIN_BASE_URL
export DECOS_ALLOWED_HOSTS="$RAW_ALLOWED_HOSTS"
export DECOS_SECRET_KEY
export CSRF_TRUSTED_ORIGINS

# === Step 6: Show results ===
echo "WAGTAILADMIN_BASE_URL set to: $WAGTAILADMIN_BASE_URL"
echo "DECOS_ALLOWED_HOSTS set to: $DECOS_ALLOWED_HOSTS"
echo "CSRF_TRUSTED_ORIGINS set to: $CSRF_TRUSTED_ORIGINS"
echo "DECOS_SECRET_KEY generated"

# === Step 7: Save to .env ===
read -p "Do you want to save these values to a .env file? (y/n): " answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    # Remove existing entries
    sed -i '/^WAGTAILADMIN_BASE_URL=/d' .env 2>/dev/null
    sed -i '/^DECOS_ALLOWED_HOSTS=/d' .env 2>/dev/null
    sed -i '/^DECOS_SECRET_KEY=/d' .env 2>/dev/null
    sed -i '/^CSRF_TRUSTED_ORIGINS=/d' .env 2>/dev/null

    {
        echo "WAGTAILADMIN_BASE_URL=\"$WAGTAILADMIN_BASE_URL\""
        echo "DECOS_ALLOWED_HOSTS=\"$DECOS_ALLOWED_HOSTS\""
        echo "DECOS_SECRET_KEY=\"$DECOS_SECRET_KEY\""
        echo "CSRF_TRUSTED_ORIGINS=$CSRF_TRUSTED_ORIGINS"
    } >> .env

    echo "Saved to .env"
fi