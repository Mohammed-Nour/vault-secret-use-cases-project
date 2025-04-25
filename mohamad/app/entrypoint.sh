#!/bin/sh

# Load environment variables from Vault template
if [ -f /vault/secrets/database-config.txt ]; then
  export $(cat /vault/secrets/database-config.txt | xargs)
fi

# Start the Flask app
exec python3 main.py
