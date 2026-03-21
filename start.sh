#!/usr/bin/env bash

python manage.py start_bots
gunicorn config.asgi:application -w 1 -k uvicorn.workers.UvicornWorker

