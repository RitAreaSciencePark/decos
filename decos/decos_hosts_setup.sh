#!/bin/bash

# Ensure the file exists
ALLOWED_HOSTS_FILE="DECOS_ALLOWED_HOSTS"
if [ ! -f "$ALLOWED_HOSTS_FILE" ]; then
    echo "Error: $ALLOWED_HOSTS_FILE not found"
    exit 1
fi

# Read all lines
readarray -t HOSTS_ARRAY < "$ALLOWED_HOSTS_FILE"

# Check if the file has at least one host
if [ ${#HOSTS_ARRAY[@]} -eq 0 ]; then
    echo "Error: DECOS_ALLOWED_HOSTS is empty"
    exit 1
fi

# Set the first host as the base URL for Wagtail
FIRST_HOST="${HOSTS_ARRAY[0]}"
export WAGTAILADMIN_BASE_URL="https://$FIRST_HOST"

# Create comma-separated list for ALLOWED_HOSTS
DECOS_ALLOWED_HOSTS=$(IFS=, ; echo "${HOSTS_ARRAY[*]}")
export DECOS_ALLOWED_HOSTS="$DECOS_ALLOWED_HOSTS"

# Output the results
echo "WAGTAILADMIN_BASE_URL set to: $WAGTAILADMIN_BASE_URL"
echo "DECOS_ALLOWED_HOSTS set to: $DECOS_ALLOWED_HOSTS"