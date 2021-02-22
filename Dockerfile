## multi-stage ###############################
ARG LANG=C
ARG APP_ROOT=/srv
ARG APP_DIR=app
ARG APP_NAME=crm
ARG DJANGO_USER=crm
ARG RUNTIME_PKGS="git bash nodejs npm libpq libjpeg openjpeg tiff freetype libffi pcre libressl libwebp lcms2 bzip2 libxml2 libxslt"
ARG BUILD_PKGS="build-base postgresql-dev zlib-dev jpeg-dev openjpeg-dev tiff-dev freetype-dev libffi-dev pcre-dev libressl-dev libwebp-dev lcms2-dev bzip2-dev readline-dev sqlite-dev libxml2-dev libxslt-dev"
ARG PIPENV_VENV_IN_PROJECT=1
ARG PYVER=3.9.2

## build ##############################################
FROM alpine:latest AS build-image

LABEL maintainer="davidn@uniquode.io"

ARG LANG
ARG APP_ROOT
ARG APP_DIR
ARG APP_NAME
ARG DJANGO_USER
ARG RUNTIME_PKGS
ARG BUILD_PKGS
ARG PIPENV_VENV_IN_PROJECT
ARG PYVER

ENV APP_ROOT=${APP_ROOT}
ENV APP_NAME=${APP_NAME}
ENV APP_DIR=${APP_DIR}
ENV DJANGO_USER=${DJANGO_USER}
ENV DJANGO_ROOT=${APP_ROOT}/${APP_NAME}
ENV PYENV_ROOT=${DJANGO_ROOT}/.pyenv
ENV PATH=${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}
ENV PIPENV_VENV_IN_PROJECT=${PIPENV_VENV_IN_PROJECT}
ENV PYVER=${PYVER}

# permanent packages we need here
RUN apk --update add ${BUILD_PKGS} ${RUNTIME_PKGS}

RUN git clone https://github.com/yyuu/pyenv.git ${PYENV_ROOT}

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

ARG LANG
ARG APP_ROOT
ARG APP_DIR
ARG APP_NAME
ARG DJANGO_USER
ARG RUNTIME_PKGS
ARG BUILD_PKGS
ARG PIPENV_VENV_IN_PROJECT
ARG PYVER

ENV APP_ROOT=${APP_ROOT}
ENV APP_NAME=${APP_NAME}
ENV APP_DIR=${APP_DIR}
ENV DJANGO_USER=${DJANGO_USER}
ENV DJANGO_ROOT=${APP_ROOT}/${APP_NAME}
ENV PYENV_ROOT=${DJANGO_ROOT}/.pyenv
ENV PATH=${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}
ENV PIPENV_VENV_IN_PROJECT=${PIPENV_VENV_IN_PROJECT}
ENV PYVER=${PYVER}
ENV DJANGO_READ_DOT_ENV_FILE=true

COPY --from=build-image ${DJANGO_ROOT} ${DJANGO_ROOT}
RUN adduser --disabled-password --home ${DJANGO_ROOT} ${DJANGO_USER}

RUN apk --update add ${RUNTIME_PKGS}

COPY ${APP_DIR}/ ${DJANGO_ROOT}/
COPY docker.env ${DJANGO_ROOT}/.env
WORKDIR ${DJANGO_ROOT}/

RUN mkdir -p ${DJANGO_ROOT}/static ${DJANGO_ROOT}/media ${DJANGO_ROOT}/logs
RUN find ${DJANGO_ROOT} -name '.DS_Store' -o -name '__pycache__' -o -name '*.py[cod]' -exec rm -rf {} +
RUN chown -R ${DJANGO_USER}:${DJANGO_USER} ${DJANGO_ROOT}

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
