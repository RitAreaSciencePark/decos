#!/bin/bash

# Generate a 50-character secure Django SECRET_KEY
DECOS_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')

echo "Your DECOS SECRET_KEY:"
echo "$DECOS_SECRET_KEY"

# Optional: Save to .env file
read -p "Do you want to save this key to a .env file? (y/n): " answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    echo "DECOS_SECRET_KEY=\"$DECOS_SECRET_KEY\"" >> .env
    echo "Saved to .env"
fi