#!/usr/bin/env bash

gunicorn config.asgi:application \
    -w 1 \
    -k uvicorn.workers.UvicornWorker \
    -b 0.0.0.0:$PORT \
    --log-level info

python manage.py start_bots

