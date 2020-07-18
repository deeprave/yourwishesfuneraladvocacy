#!/bin/sh
[ -f .env ] && source .env || { echo ".env does not exist!" && exit 1; }

function usage {
  msg="$*"
  [ ! -z "${msg}" ] && echo ${msg} 1>&2
  cat <<USAGE
`basename "$0"`: [options]
Options:
  -h    this help message
  -r    reset postgres docker data volume for this project
  -R    reset all docker data volumes for this project
  -b    (re)build the app docker container
  -g    initialise and update a local git repository

** note: to set the postgres admin password a postgres data reset is required
USAGE
}

dc_reset=0
dc_reset_all=0
dc_build_app=1
git_init=0

args=`getopt hgbrR $*` || { usage && exit 2; }
set -- $args
for opt
do
	case "$opt" in
		-h)
			usage
			exit 1
			;;
    -b)
      dc_build_app=1
      shift
      ;;
	  -R)
	    dc_reset_all=1
	    dc_reset=1
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
  esac
done

if [ ${dc_reset} != 0 ]; then
  # check to see if anything is running
  if [ ! -z "`docker ps -q -f name=${COMPOSE_PROJECT_NAME}`" ]; then
    echo '*>' Stopping all running containers
    docker-compose down
  fi
  if [ ${dc_reset_all} != 0 ]; then
    # remove all project volumes
    volumes=`docker volume ls -q -f name=${COMPOSE_PROJECT_NAME}`
  else
    # remove project postgres volume
    volumes=`docker volume ls -q -f name=${COMPOSE_PROJECT_NAME}_data-pgdata`
  fi
  if [ ! -z "${volumes}" ]; then
    echo '*>' Removing volumes ${volumes}
    docker volume rm ${volumes}
  fi
fi

if [ -z "`docker ps -q -f name=${COMPOSE_PROJECT_NAME}`" ]; then
  echo '*>' Starting ${COMPOSE_PROJECT_NAME} service containers
  docker-compose -f docker-compose-services.yml up -d
  echo '*>' Waiting a few seconds for the database to come up
  sleep 10.0
fi

# create a role with a user, use permission inheritance for convenience
PGPASSWORD="${POSTGRES_PASSWORD}" psql -h ${DBHOST} -p ${DBPORT} postgres postgres <<SQL
create role ${DBROLE} createdb;
create user ${DBUSER} createrole inherit password '${DBPASS}';
grant ${DBROLE} to ${DBUSER};
alter role ${DBROLE} set client_encoding to 'utf8';
alter role ${DBROLE} set default_transaction_isolation to 'read committed';
alter role ${DBROLE} set timezone to 'UTC';
SQL

# create the database(es)
for db_name in ${DBNAME}
do
  echo "Creating database: ${db_name}"
	PGPASSWORD="${POSTGRES_PASSWORD}" psql -h ${DBHOST} -p ${DBPORT} postgres postgres <<SQL
create database ${db_name} with owner ${DBROLE};
grant all privileges on database ${db_name} to ${DBROLE};
SQL
done

# do intialisation in sub-shell
(
  cd ${APP_DIR}
  # do the initial migration
  ./manage.py migrate
  # add the superuser
  ./manage.py createsuperuser
)

if [ ${dc_build_app} != 0 ]; then

  docker-compose build app

fi

if [ ${git_init} != 0 ]; then

  # Initialise a git repo
  # Remove /.env exclusion - the project needs it
  while read -r line
    [[ ${line} != '/.env' ]] echo "${line}"
  do
  done < .gitignore > .gitignore.new
  mv .gitignore.new .gitignore

  git init .
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
