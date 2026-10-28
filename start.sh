#!/usr/bin/env bash

# start.sh - Script to run the ASReview Reviewer Analytics Dashboard

# Change to the script's directory
cd "$(dirname "$0")"

# Load configuration from config.env and .env if they exist
set -a
[ -f config.env ] && source config.env
[ -f .env ] && source .env
set +a

# Default configuration (can be overridden by setting these environment variables before running the script or in the .env files)
export ASREVIEW_BASE_URL=${ASREVIEW_BASE_URL:-"http://127.0.0.1:8081"}
export PORT=${PORT:-5050}
export WORKERS=${WORKERS:-4}

echo "Starting ASReview Analytics Dashboard..."
echo "ASReview Backend Endpoint: $ASREVIEW_BASE_URL"
echo "Listening on Port: $PORT"
echo "Number of Gunicorn Workers: $WORKERS"
echo "----------------------------------------"

# Run the app with gunicorn
exec gunicorn -w "$WORKERS" -b "0.0.0.0:$PORT" "app:app"
