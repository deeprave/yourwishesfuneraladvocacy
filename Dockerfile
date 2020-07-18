FROM python:3.8 as python3-wagtail
LABEL maintainer="davidn@uniquode.io"

ARG APP_DIR=app
ARG APP_NAME=app
ARG APP_ROOT=/srv
ARG DJANGO_MODE=dev
ARG DJANGO_USER=cms
ARG DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
ARG REDIS_CACHE=redis://127.0.0.1:6379/0
ARG REDIS_SESSION=redis://127.0.0.1:6379/1
ARG DATABASE_URL=postgres://user:password@127.0.0.1:5432/database

ENV APP_ROOT=${APP_ROOT} APP_NAME=${APP_NAME} APP_DIR=${APP_DIR}
ENV DJANGO_MODE=${DJANGO_MODE} DJANGO_ROOT=${APP_ROOT}/${APP_NAME} DJANGO_USER=${DJANGO_USER} DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
ENV REDIS_CACHE=${REDIS_CACHE} REDIS_SESSION=${REDIS_SESSION} DATABASE_URL=${DATABASE_URL}
ENV PYTHONUNBUFFERED 1

RUN mkdir -p ${DJANGO_ROOT} ${DJANGO_ROOT}/static ${DJANGO_ROOT}/media

WORKDIR ${DJANGO_ROOT}/

COPY ./requirements.txt ${DJANGO_ROOT}/requirements.txt

RUN pip install -q -U pip && \
	pip install -r ${DJANGO_ROOT}/requirements.txt && \
	pip install uvicorn && \
    useradd ${DJANGO_USER} && \
	chown -R ${DJANGO_USER} ${DJANGO_ROOT}

COPY ${APP_DIR}/ ${DJANGO_ROOT}/

WORKDIR ${DJANGO_ROOT}/
USER ${DJANGO_USER}
VOLUME ["${DJANGO_ROOT}", "${DJANGO_ROOT}/media", "${DJANGO_ROOT}/static"]

EXPOSE 8000

CMD exec uvicorn ${APP_NAME}.asgi:application --host 0.0.0.0 --port 8000 --workers 3 --access-log --use-colors
