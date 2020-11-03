#!/bin/sh
[ -f ./.env ] && source ./.env || { echo ".env does not exist!" && exit 1; }

function usage {
  msg="$*"
  [ ! -z "${msg}" ] && echo ${msg} 1>&2
  cat <<USAGE
`basename "$0"`: [options]
Options:
  -h    this help message
  -S    services run in docker (docker-compose-services)
  -r    reset postgres data
  -R    reset all docker data volumes for this project
  -b    (re)build the app docker container
  -g    update a local git repository (initialise if necessary)
  -m    run database migrations

** note: to set the postgres admin password a postgres data reset is required
USAGE
}

dc_reset=0
dc_reset_all=0
dc_build_app=0
dc_docker=0
dc_migrate=0
git_init=0

SELECT_DATABASE=

args=`getopt hSbRrgm $*` || { usage && exit 2; }
set -- $args
for opt
do
  case "$opt" in
    -h)
      usage
      exit 1
      ;;
    -S)
      dc_docker=1
      SELECT_DATABASE="-h ${DBHOST}"
      shift
      ;;
    -b)
      dc_build_app=1
      shift
      ;;
    -R)
      dc_reset_all=1
      dc_reset=1
      dc_docker=1
      shift
      ;;
    -r)
      dc_reset=1
      shift
      ;;
    -g)
      git_init=1
      shift
      ;;
    -m)
      dc_migrate=1
      shift
      ;;
  esac
done

if [ ${dc_reset} != 0 ]; then
  if [ ${dc_docker} != 0 -a ${dc_reset_all} != 0 ]; then
    # check to see if anything is running
    if [ ! -z "`docker ps -q -f name=${COMPOSE_PROJECT_NAME}`" ]; then
      echo '*>' Stopping all running containers
      docker-compose down
    fi
    # remove all project volumes
    volumes=`docker volume ls -q -f name=${COMPOSE_PROJECT_NAME}`
    if [ ! -z "${volumes}" ]; then
      echo '*>' Removing volumes ${volumes}
      docker volume rm ${volumes}
    fi
  else
    PGPASSWORD="${POSTGRES_PASSWORD}" psql ${SELECT_DATABASE} -p ${DBPORT} postgres postgres <<SQL
drop database ${DBNAME};
drop user ${DBUSER};
drop role ${DBROLE};
SQL
  fi
fi

if [ ${dc_docker} != 0 ]; then
  if [ -z "`docker ps -q -f name=${COMPOSE_PROJECT_NAME}`" ]; then
    echo '*>' Starting ${COMPOSE_PROJECT_NAME} service containers
    docker-compose -f docker-compose-services.yml up -d
    echo '*>' Waiting a few seconds for the database to come up
    sleep 10.0
  fi
fi

# create a role with a user, use permission inheritance for convenience
echo "Setting up database roles"
PGPASSWORD="${POSTGRES_PASSWORD}" psql ${SELECT_DATABASE} -p ${DBPORT} postgres postgres <<SQL
create role ${DBROLE} createdb;
create user ${DBUSER} createrole inherit password '${DBPASS}';
grant ${DBROLE} to ${DBUSER};
alter role ${DBROLE} set client_encoding to 'utf8';
alter role ${DBROLE} set default_transaction_isolation to 'read committed';
alter role ${DBROLE} set timezone to 'UTC';
SQL

# create the database(es)
echo "Creating database: ${DBNAME}"
PGPASSWORD="${POSTGRES_PASSWORD}" psql ${SELECT_DATABASE} -p ${DBPORT} postgres postgres <<SQL
create database ${DBNAME} with owner ${DBROLE};
grant all privileges on database ${DBNAME} to ${DBROLE};
SQL

if [ ${dc_migrate} != 0 ]; then
  cd ${APP_DIR} && (
    ./manage.py makemigrations
    ./manage.py migrate
    ./manage.py createsuperuser
    ./manage.py collectstatic --no-input
  )
fi

if [ ${dc_build_app} != 0 ]; then

  docker-compose build app

fi


if [ ${git_init} != 0 ]; then

  # Initialise a git repo
  [ ! -d .git ] && git init .
  git add -A
  git commit -m 'Initial commit'

fi


# done!
cat <<WELCOME

  Initial Wagtail setup is done - welcome to your new development environment!

  Webserver will be available after running:

    $ cd ${APP_DIR}
    $ ./manage.py runserver

  Runs the local development server (non-async)

  - OR -

    $ docker-compose up -d app

  Use uvicorn to serve the app (async)

WELCOME
