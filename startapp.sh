#!/bin/sh
cd ${DJANGO_ROOT}
npm install
python manage.py migrate
python manage.py collectstatic --no-input
exec uvicorn ${APP_NAME}.asgi:application --host 0.0.0.0 --port 8000 --workers 3 --access-log --use-colors
