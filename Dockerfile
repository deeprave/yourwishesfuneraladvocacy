FROM alpine:latest
LABEL maintainer="davidn@uniquode.io"

RUN apk --update add python3 py3-pip py3-wheel nodejs npm && \
    npm install -g yarn && \
    cd /usr/bin && ln -sf python3 python && ln -sf pip3 pip

COPY ./requirements.txt /tmp/requirements.txt

ARG APP_DIR=app
ARG APP_NAME=app
ARG APP_ROOT=/srv
ARG DJANGO_MODE=dev
ARG DJANGO_USER=cms
ARG DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
ARG REDIS_CACHE=redis://redis:6379/0
ARG REDIS_SESSION=redis://redis:6379/1
ARG DATABASE_URL=postgres://user:password@db:5432/app
ARG DEVLIBS="build-base python3-dev postgresql-dev zlib-dev jpeg-dev openjpeg-dev tiff-dev freetype-dev libffi-dev pcre-dev libressl-dev libwebp-dev lcms2-dev"

ENV APP_ROOT=${APP_ROOT} APP_NAME=${APP_NAME} APP_DIR=${APP_DIR}
ENV DJANGO_MODE=${DJANGO_MODE} DJANGO_ROOT=${APP_ROOT}/${APP_NAME} DJANGO_USER=${DJANGO_USER} DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
ENV REDIS_CACHE=${REDIS_CACHE} REDIS_SESSION=${REDIS_SESSION} DATABASE_URL=${DATABASE_URL}
ENV PYTHONUNBUFFERED 1

RUN apk add libpq libjpeg openjpeg tiff freetype libffi pcre libressl libwebp lcms2 ${DEVLIBS} && \
    pip install -q -U pip setuptools pip && \
    pip install -r /tmp/requirements.txt && \
    pip install uvicorn && \
    apk del ${DEVLIBS} && \
    rm -rf /root/.cache /var/cache/apk/* && \
    adduser --disabled-password --home ${DJANGO_ROOT} ${DJANGO_USER} && \
    mkdir -p ${DJANGO_ROOT}/static ${DJANGO_ROOT}/media && \
    chown -R ${DJANGO_USER} ${DJANGO_ROOT}

WORKDIR ${DJANGO_ROOT}/

COPY ${APP_DIR}/ ${DJANGO_ROOT}/

USER ${DJANGO_USER}
VOLUME ["${DJANGO_ROOT}", "${DJANGO_ROOT}/media", "${DJANGO_ROOT}/static"]

EXPOSE 8000

CMD exec uvicorn ${APP_NAME}.asgi:application --host 0.0.0.0 --port 8000 --workers 3 --access-log --use-colors
