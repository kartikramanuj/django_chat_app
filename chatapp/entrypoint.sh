#!/bin/sh

# Run migrations and start Django app
python manage.py migrate
# python manage.py runserver 0.0.0.0:8000
uvicorn backend.asgi:application --host 0.0.0.0 --port 8000 --reload --log-level debug
