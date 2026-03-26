#!/usr/bin/env bash
set -e  # fail fast if anything breaks
set -x  # show commands in logs

echo "Setting webhooks..."
python manage.py set_bot_webhooks

echo "Starting gunicorn..."
exec gunicorn config.asgi:application \
  -w 1 \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:$PORT