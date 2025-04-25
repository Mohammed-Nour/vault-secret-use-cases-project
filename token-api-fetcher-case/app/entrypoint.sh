#!/bin/sh
set -e

# Load API_URL
if [ -f /vault/secrets/api_url ]; then
  export API_URL=$(cat /vault/secrets/api_url | xargs)
else
  echo " /vault/secrets/api_url not found; API_URL may be unset"
fi

# Load EXPECTED_TOKEN
if [ -f /vault/secrets/token ]; then
  export EXPECTED_TOKEN=$(cat /vault/secrets/token | xargs)
else
  echo "  /vault/secrets/token not found; EXPECTED_TOKEN may be unset"
fi

# Start the Flask app
exec python3 main.py