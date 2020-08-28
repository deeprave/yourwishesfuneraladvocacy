#!/bin/sh
cd ${DJANGO_ROOT}
npm install
python manage.py migrate
python manage.py collectstatic --no-input
# exec uvnicorn ${APP_NAME}.wsgi:application --host 0.0.0.0 --port 8000 --workers 5 --access-log --use-colors
exec gunicorn ${APP_NAME}.wsgi:application --bind 0.0.0.0:8000 --worker-connections 5 --access-logfile /dev/stdout --error-logfile /dev/stdout
