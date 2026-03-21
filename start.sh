#!/usr/bin/env bash
set -e  # fail fast if anything breaks
set -x  # show commands in logs

echo "Starting bots..."
python manage.py start_bots

echo "Starting gunicorn..."
exec gunicorn config.asgi:application \
  -w 1 \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:$PORT