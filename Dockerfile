FROM alpine:latest
LABEL maintainer="davidn@uniquode.io"

RUN apk --update add python3 py3-pip py3-wheel nodejs npm && \
    cd /usr/bin && ln -sf python3 python && ln -sf pip3 pip

COPY ./requirements.txt /tmp/requirements.txt

ARG APP_DIR=app
ARG APP_NAME=app
ARG APP_ROOT=/srv
ARG DJANGO_MODE=dev
ARG DJANGO_USER=cms
ARG DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
ARG DJANGO_LOGDIR=/srv/logs/app
ARG REDIS_CACHE=redis://redis:6379/0
ARG REDIS_SESSION=redis://redis:6379/1
ARG DATABASE_URL=postgres://user:password@db:5432/app
ARG EMAIL_HOST_USER=${EMAIL_HOST_USER}
ARG EMAIL_POST_PASSWORD=${EMAIL_HOST_PASSWORD}
ARG EMAIL_HOST=smtp.google.com
# removable baggage required to build python modules
ARG DEVLIBS="build-base python3-dev postgresql-dev zlib-dev jpeg-dev openjpeg-dev tiff-dev freetype-dev libffi-dev pcre-dev libressl-dev libwebp-dev lcms2-dev"

# set up the django runtime environment

ENV APP_ROOT=${APP_ROOT} APP_NAME=${APP_NAME} APP_DIR=${APP_DIR} PYTHONUNBUFFERED=1
ENV DJANGO_MODE=${DJANGO_MODE} DJANGO_ROOT=${APP_ROOT}/${APP_NAME} DJANGO_USER=${DJANGO_USER}
ENV EMAIL_HOST_USER=${EMAIL_HOST_USER} EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD}
ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY} DJANGO_LOGDIR=${DJANGO_ROOT}/logs
ENV REDIS_CACHE=${REDIS_CACHE} REDIS_SESSION=${REDIS_SESSION} DATABASE_URL=${DATABASE_URL}

# install runtime requirements and dev, but remove dev before creating this layer

RUN apk add libpq libjpeg openjpeg tiff freetype libffi pcre libressl libwebp lcms2 ${DEVLIBS} && \
    pip install -q -U pip setuptools pip && \
    pip install -r /tmp/requirements.txt && \
    pip install gunicorn && \
    apk del ${DEVLIBS} && \
    rm -rf /root/.cache /var/cache/apk/*

# create the user so we don't run as root

RUN mkdir -p ${DJANGO_ROOT} && adduser --disabled-password --home ${DJANGO_ROOT} ${DJANGO_USER}

WORKDIR ${DJANGO_ROOT}/
COPY ${APP_DIR}/ ${DJANGO_ROOT}/

# create the generated content folders and change owner to runtime user

RUN mkdir -p static media logs && chown -R ${DJANGO_USER}:${DJANGO_USER} ${DJANGO_ROOT}

# startup.sh takes care of:
# 1. running possible new database migrations
# 2. compiling sass to static css
# 3. collectstatic to update static files

COPY startapp.sh /

# export these volumes as root

VOLUME ["${DJANGO_ROOT}", "${DJANGO_ROOT}/logs", "${DJANGO_ROOT}/media", "${DJANGO_ROOT}/static"]

USER ${DJANGO_USER}
EXPOSE 8000

CMD /startapp.sh
