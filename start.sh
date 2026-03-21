#!/usr/bin/env bash

python manage.py start_bots &
python manage.py set_bot_webhooks
gunicorn config.asgi:application -w 1 -k uvicorn.workers.UvicornWorker

