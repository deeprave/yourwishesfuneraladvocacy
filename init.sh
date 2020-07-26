#!/bin/sh
# init.sh
# Initialise a wagtail project using current and compatible versions of Django and Wagtail

# set defaults for .env
COMPOSE_PROJECT_NAME=myapp
COMPOSE_FILE=docker-compose-services.yml:docker-compose.yml
APP_NAME=myapp
APP_DIR=myapp
APP_ROOT=/srv
DBHOST=127.0.0.1
DBPORT=5432
DBROLE=myappadmin
DBNAME=myapp
DBUSER=myapp
DBPASS=my-secret-password-54321
POSTGRES_PASSWORD=my-sa-password-54321
RDHOST=127.0.0.1
RDPORT=6379
RD0=0
RD1=1
REDIS_CACHE=redis://${RDHOST}:${RDPORT}/${RD0}
REDIS_SESSION=redis://${RDHOST}:${RDPORT}/${RD1}
DATABASE_URL=postgres://${DBUSER}:${DBPASS}@${DBHOST}:${DBPORT}/${DBNAME}
DJANGO_SECRET_KEY=
DJANGO_MODE=dev
BASE_URL='http://example.com'
EXT_ROOT=
EXT_STATIC=
EXT_MEDIA=
EXT_DOCUMENTS=

# if there i an existing .env, source it to retain values as defaults across sessions
[ -f ./.env ] && source ./.env

function usage {
  msg="$*"
  [ ! -z "${msg}" ] && echo ${msg} 1>&2
  cat <<USAGE
`basename "$0"`: [options] [appname]
General Options:
 -P <name>      set project name     | -S             random SECRET_KEY
 -a <name>      set app name         | -d <directory> set app subdir
 -U <url>       set site base url    | -R             generate passwords
 -h             this help message    | -D             run services in docker
PostgreSQL Options:                  | Redis Options:
 -i <hostname>  hostname (use IP)    |  -I <hostname>  hostname (use IP)
 -p <port>      port                 |  -P <port>      port
 -n <db_name>   database             |  -c <n>         cache db [0-15]
 -g <rolename>  app role             |  -s <n>         session db [0-15]
 -u <username>  app username         |
 -w <password>  app password         |  -E <n>         prefix default database
 -G <password>  sa postgres password |                 and redis ports [1-6]
USAGE
[ -z "${VIRTUAL_ENV}" ] && echo; echo "** WARNING: no virtualenv detected **"
}

function secretkey {
  LC_ALL=C openssl rand 50 | base64
}

function random_password {
  LC_ALL=C tr -dc '[:alnum:]' </dev/urandom | dd bs=16 count=1 2>/dev/null
}

function lowercase {
  echo "$1" | tr '[:upper:]' '[:lower:]'
}

# working variables
dir_set=0
name_set=0
role_set=0
user_name=0
user_pass=0
psql_pass=0
sleep_interval=5.0
dc_services=0

# parse the command line
args=`getopt hpDSe:E:a:d:i:p:u:w:g:rRI:P:c:s:E:U: $*` || { usage && exit 2; }
set -- $args
for opt
do
  case "$opt" in
    -h)
      usage
      exit 1
      ;;
    -D)
      dc_services=1
      shift
      ;;
    -P)
      COMPOSE_PROJECT_NAME=${2}
      shift; shift
      ;;
    -a)
      APP_NAME=`lowercase ${2}` && { [ ${dir_set} == 0 ] && APP_DIR="${2}" && dir_set=1; }
      shift; shift
      ;;
    -U)
      BASE_URL=${2}
      shift; shift
      ;;
    -S)
      DJANGO_SECRET_KEY=`secretkey`
      shift
      ;;
    -d)
      APP_DIR=${2} && dir_set=1
      shift; shift
      ;;
    -n)
      DBNAME=${2} && name_set=1
      shift; shift
      ;;
    -i)
      DBHOST=${2}
      shift; shift
      ;;
    -p)
      DBPORT=${2}
      shift; shift
      ;;
    -g)
      DBROLE=${2} && role_set=1
      [ ${user_name} == 0 ] && DBUSER=${2}user && user_name=1
      [ ${name_set} == 0 ] && DBNAME=${2} && name_set=1
      shift; shift
      ;;
    -u)
      DBUSER=${2} && user_name=1
      [ ${name_set} == 0 ] && DBNAME=${2} && name_set=1
      shift; shift
      ;;
    -w)
      DBPASS=${2} && user_pass=1
      shift; shift
      ;;
    -r)
      DBPASS="`random_password`" && user_pass=1
      shift
      ;;
    -G)
      POSTGRES_PASSWORD="${2}" && psql_pass=1
      shift; shift
      ;;
    -R)
      POSTGRES_PASSWORD="`random_password`" && psql_pass=1
      [ ${user_pass} == 0 ] && DBPASS="`random_password`" && user_pass=1
      shift
      ;;
    -I)
      RDHOST=${2} 
      shift; shift
      ;;
    -P)
      RDPORT=${2} 
      shift; shift
      ;;
    -E)
      DBPORT=${2}5432
      RDPORT=${2}6379
      shift; shift
      ;;
    -c)
      RD0=${2} 
      shift; shift
      ;;
    -s)
      RD1=${2} 
      shift; shift
      ;;
    --)
      shift
      break
      ;;
  esac
done

rest=${*}
if [ ! -z "${rest}" ]; then
  COMPOSE_PROJECT_NAME=${rest}
  APP_NAME=`lowercase ${rest}`
  [ ${dir_set} == 0 ] && APP_DIR=${APP_NAME}
  [ ${name_set} == 0 ] && DBNAME=${APP_NAME}
  [ ${user_name} == 0 ] && DBUSER=${APP_NAME}_user
  [ ${role_set} == 0 ] && DBROLE=${APP_NAME}
  [ ${user_pass} == 0 ] && DBPASS="`random_password`"
  [ ${psql_pass} == 0 ] && POSTGRES_PASSWORD="`random_password`"
  DJANGO_SECRET_KEY=`secretkey`
fi

[ -z ${EXT_ROOT} ]      && EXT_ROOT=${PWD}
[ -z ${EXT_STATIC} ]    && EXT_STATIC=${EXT_ROOT}/${APP_DIR}/static
[ -z ${EXT_MEDIA} ]     && EXT_MEDIA=${EXT_ROOT}/${APP_DIR}/media
[ -z ${EXT_DOCUMENTS} ] && EXT_DOCUMENTS=${EXT_ROOT}/${APP_DIR}/documents

[ -z "${VIRTUAL_ENV}" ] && { echo "this script requires an active virtualenv"; exit 3; }

if [ ${dc_docker} != 0 ]; then
  COMPOSE_FILE=docker-compose.yml
else
  COMPOSE_FILE=docker-compose-services.yml:docker-compose.yml
fi

cat <<ENV | tee .env
COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME}
COMPOSE_FILE=${COMPOSE_FILE}
APP_NAME=${APP_NAME}
APP_DIR=${APP_DIR}
APP_ROOT=${APP_ROOT}
DBHOST=${DBHOST}
DBPORT=${DBPORT}
DBROLE=${DBROLE}
DBNAME=${DBNAME}
DBUSER=${DBUSER}
DBPASS=${DBPASS}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
RDHOST=${RDHOST}
RDPORT=${RDPORT}
RD0=${RD0}
RD1=${RD1}
DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
DJANGO_MODE=${DJANGO_MODE}
REDIS_CACHE=redis://${RDHOST}:${RDPORT}/${RD0}
REDIS_SESSION=redis://${RDHOST}:${RDPORT}/${RD1}
DATABASE_URL=postgres://${DBUSER}:${DBPASS}@${DBHOST}:${DBPORT}/${DBNAME}
BASE_URL=${BASE_URL}
EXT_ROOT=${EXT_ROOT}
EXT_STATIC=${EXT_STATIC}
EXT_MEDIA=${EXT_MEDIA}
ENV

echo ""
read -p "Check values above - press ENTER to continue or ^C to abort."
echo ""

function action {
  msg="$*"
  echo '=>' About to $msg
  sleep ${sleep_interval}
  echo '*>' $msg
}

action install python dependencies
pip install -q -U pip setuptools wheel
pip install -q -r requirements-dev.txt

action create wagtail project
mkdir -p ${APP_DIR}
wagtail start ${APP_NAME} ${APP_DIR}

git_ignore=${APP_DIR}/.gitignore
echo '# no version control in these dirs' > ${git_ignore}
for content in media static
do
  mkdir -p ${APP_DIR}/${content}
  echo /${content}/ >> ${git_ignore}
done

# tidy & additions
action adjust wagtail settings
rm -f ${APP_DIR}/requirements.txt ${APP_DIR}/Dockerfile
python wagtail_settings.py ${APP_DIR}

if [ ${dc_services} != 0 ]; then
# start the database and cache
  action start services
  docker-compose -f docker-compose-services.yml up -d
fi
