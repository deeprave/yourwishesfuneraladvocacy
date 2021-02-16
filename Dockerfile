## multi-stage ###############################
ARG LANG=C
ARG APP_ROOT=/srv
ARG APP_DIR=code
ARG APP_NAME=crm
ARG DJANGO_MODE=dev
ARG DJANGO_USER=crm
ARG RUNTIME_PKGS="git bash nodejs npm libpq libjpeg openjpeg tiff freetype libffi pcre libressl libwebp lcms2 bzip2 libxml2 libxslt"
ARG BUILD_PKGS="build-base postgresql-dev zlib-dev jpeg-dev openjpeg-dev tiff-dev freetype-dev libffi-dev pcre-dev libressl-dev libwebp-dev lcms2-dev bzip2-dev readline-dev sqlite-dev libxml2-dev libxslt-dev"
ARG PIPENV_VENV_IN_PROJECT=1
ARG PYVER=3.9.1

## build ##############################################
FROM alpine:latest AS build-image

LABEL maintainer="davidn@uniquode.io"

ARG LANG
ARG APP_ROOT
ARG APP_DIR
ARG APP_NAME
ARG DJANGO_MODE
ARG DJANGO_USER
ARG RUNTIME_PKGS
ARG BUILD_PKGS
ARG PIPENV_VENV_IN_PROJECT
ARG PYVER

# permanent packages we need here
RUN apk --update add ${BUILD_PKGS} ${RUNTIME_PKGS}

ENV DJANGO_ROOT=${APP_ROOT}/${APP_NAME}
ENV PYENV_ROOT=${DJANGO_ROOT}/.pyenv
RUN git clone https://github.com/yyuu/pyenv.git ${PYENV_ROOT}
ENV PATH=${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}

ENV DJANGO_USER=${DJANGO_USER}
RUN adduser --disabled-password --home ${DJANGO_ROOT} ${DJANGO_USER}
RUN mkdir -p ${DJANGO_ROOT}

RUN pyenv install ${PYVER}
RUN pyenv global ${PYVER}
RUN pip install -U pip setuptools wheel unicode pipenv

WORKDIR ${DJANGO_ROOT}/

COPY Pipfile .
COPY Pipfile.lock .

ENV HOME=${DJANGO_ROOT}
ENV LANG=${LANG} PIPENV_VENV_IN_PROJECT=${PIPENV_VENV_IN_PROJECT}
RUN pipenv --python ${PYVER} install --deploy


## runtime ##############################################
FROM alpine:latest AS runtime-image
COPY --from=build-image ${DJANGO_ROOT} ${DJANGO_ROOT}

ARG LANG
ARG APP_ROOT
ARG APP_DIR
ARG APP_NAME
ARG PIPENV_VENV_IN_PROJECT
ARG RUNTIME_PKGS
ARG DJANGO_USER

RUN apk --update add ${RUNTIME_PKGS}

ARG DJANGO_SECRET_KEY
ARG TOKEN_SECRET_KEY
ARG DATABASE_URL
ARG MEMCACHE_URL
ARG CACHE_URL
ARG EMAIL_HOST
ARG EMAIL_HOST_USER
ARG EMAIL_HOST_PASSWORD
ARG EMAIL_URL
ARG DEFAULT_FROM_EMAIL
ARG MARKETING_REPLY_EMAIL
ARG PASSWORD_RESET_MAIL_FROM_USER
ARG ADMIN_EMAIL

ARG DJANGO_MODE
ARG S3_API_ENDPOINT
ARG S3_API_BUCKET
ARG S3_API_KEY
ARG S3_API_SECRET
ARG STRIPE_PUBLIC_KEY
ARG STRIPE_PRIVATE_KEY

ENV LANG=${LANG} PIPENV_VENV_IN_PROJECT=${PIPENV_VENV_IN_PROJECT}
ENV APP_ROOT=${APP_ROOT} APP_NAME=${APP_NAME} APP_DIR=${APP_DIR} PYTHONUNBUFFERED=1
ENV DJANGO_ROOT=${APP_ROOT}/${APP_NAME}
ENV PYENV_ROOT=${DJANGO_ROOT}/.pyenv
ENV PATH=${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}
ENV DJANGO_USER=${DJANGO_USER} DJANGO_LOGDIR=${APP_ROOT}/logs/${APP_NAME} DJANGO_MODE=${DJANGO_MODE}

WORKDIR ${DJANGO_ROOT}/
COPY ${APP_DIR}/ ${DJANGO_ROOT}/
RUN mkdir -p ${DJANGO_ROOT}/static ${DJANGO_ROOT}/media ${DJANGO_ROOT}/logs
RUN find ${DJANGO_ROOT} -name '.DS_Store' -o -name '__pycache__' -o -name '*.py[cod]' -exec rm -rf {} +
RUN chown -R ${DJANGO_USER}:${DJANGO_USER} ${DJANGO_ROOT}

# django configuration
ENV EMAIL_HOST=${EMAIL_HOST} EMAIL_HOST_USER=${EMAIL_HOST_USER} EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD}
ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY} TOKEN_SECRET_KEY=${TOKEN_SECRET_KEY} DJANGO_LOGDIR=${DJANGO_ROOT}/logs
ENV CACHE_URL=${CACHE_URL} MEMCACHE_URL=${MEMCACHE_URL} DATABASE_URL=${DATABASE_URL} EMAIL_URL=${EMAIL_URL}
ENV DEFAULT_FROM_EMAIL=${DEFAULT_FROM_EMAIL} MARKETING_REPLY_EMAIL=${MARKETING_REPLY_EMAIL}
ENV PASSWORD_RESET_MAIL_FROM_USER=${PASSWORD_RESET_MAIL_FROM_USER} ADMIN_EMAIL=${ADMIN_EMAIL}
ENV S3_API_ENDPOINT=${S3_API_ENDPOINT} S3_API_BUCKET=${S3_API_BUCKET} S3_API_KEY=${S3_API_KEY} S3_API_SECRET=${S3_API_SECRET}
ENV STRIPE_PUBLIC_KEY=${STRIPE_PUBLIC_KEY} STRIPE_PRIVATE_KEY=${STRIPE_PRIVATE_KEY}

# startup.sh takes care of:
# 1. running possible new database migrations
# 2. compiling sass to static css
# 3. collectstatic to update static files

COPY startapp.sh /

USER ${DJANGO_USER}

# export these volumes
VOLUME ["${DJANGO_ROOT}", "${DJANGO_ROOT}/logs", "${DJANGO_ROOT}/media", "${DJANGO_ROOT}/static"]

EXPOSE 8000

CMD /startapp.sh
