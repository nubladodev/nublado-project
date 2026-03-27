#!/usr/bin/env bash
set -e  # fail fast if anything breaks
set -x  # show commands in logs

echo "Setting webhooks..."
python manage.py set_bot_webhooks

echo "Starting gunicorn with 2 workers..."
exec gunicorn config.asgi:application \
  -k uvicorn.workers.UvicornWorker \
  -w 2 \
  -b 0.0.0.0:$PORT \
  --timeout 120