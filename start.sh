#!/usr/bin/env bash
set -x  # shows every command

echo "Starting bots..."
python manage.py start_bots

echo "Starting gunicorn..."
gunicorn config.asgi:application \
  -w 1 \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:$PORT