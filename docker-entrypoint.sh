#!/bin/bash
set -e

# Load configuration if provided via environment files
set -a
[ -f config.env ] && source config.env
[ -f .env ] && source .env
set +a

export PORT=${PORT:-5050}
export WORKERS=${WORKERS:-4}

echo "Starting ASReview Analytics Dashboard on Port: $PORT"

# Start Gunicorn in the background
gunicorn -w "$WORKERS" -b "0.0.0.0:$PORT" "app:app" &

# Wait for the flask app to come up
sleep 3

# If a Cloudflare Tunnel token is provided, start the tunnel
if [ -n "$TUNNEL_TOKEN" ]; then
    echo "Starting Cloudflare Tunnel..."
    cloudflared tunnel --no-autoupdate run --token "$TUNNEL_TOKEN"
else
    echo "No TUNNEL_TOKEN provided. Dashboard is only available locally on port $PORT."
    # Wait for any background jobs (Gunicorn) so the container doesn't exit
    wait -n
fi
