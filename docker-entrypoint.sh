#!/bin/bash
set -e

export PORT=${PORT:-5050}
export WORKERS=${WORKERS:-4}

echo "Starting ASReview Analytics Dashboard on Port: $PORT"

# Start Gunicorn (exec replaces the shell process with gunicorn)
exec gunicorn -w "$WORKERS" -b "0.0.0.0:$PORT" "app:app"
