#!/bin/bash
cd ${DJANGO_ROOT}
source .venv/bin/activate
[ -f package.json ] && npm install
python manage.py migrate
python manage.py sass sass_src/ cms/static/scss/
python manage.py collectstatic --no-input
# exec uvnicorn ${APP_NAME}.wsgi:application --host 0.0.0.0 --port 8000 --workers 5 --access-log --use-colors
#exec uwsgi --chdir ${DJANGO_ROOT} --wsgi-file ${APP_NAME}/wsgi.py uwsgi.ini
exec gunicorn ${APP_NAME}.wsgi:application --bind 0.0.0.0:8000 --worker-connections 5 --access-logfile - --error-logfile - --log-level debug
