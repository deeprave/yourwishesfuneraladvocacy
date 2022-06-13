#!/usr/bin/env bash
: ${DOTENV:=./.env}
[ -f ./.env ] && source ${DOTENV} || { echo "${DOTENV} does not exist!" && exit 1; }
[[ ! -z $DBHOST ]] && SELECT_DATABASE=${SELECT_DATABASE:-"-h ${DBHOST}"}

echo "==> Force remove connections to ${DBNAME} (if any)"
PGPASSWORD="${POSTGRES_PASSWORD}" psql ${SELECT_DATABASE} -p ${DBPORT} -U ${POSTGRES_USER} postgres <<SQL
SELECT pg_terminate_backend(pid) FROM postgres.pg_catalog.pg_stat_activity WHERE datname='${DBNAME}';
SQL

if [ "$1" == "-r" ]; then
  echo "==> Dropping database ${DBNAME} and roles"
PGPASSWORD="${POSTGRES_PASSWORD}" psql ${SELECT_DATABASE} -p ${DBPORT} -U ${POSTGRES_USER} postgres <<SQL || exit 2
drop database ${DBNAME};
drop user ${DBUSER};
drop role ${DBROLE};
SQL
fi

# create a role with a user, use permission inheritance for convenience
echo "==> Setting up database roles"
PGPASSWORD="${POSTGRES_PASSWORD}" psql ${SELECT_DATABASE} -p ${DBPORT} -U ${POSTGRES_USER} postgres <<SQL
create role ${DBROLE};
create user ${DBUSER} createdb inherit password '${DBPASS}';
grant ${DBROLE} to ${DBUSER};
alter role ${DBROLE} set client_encoding to 'utf8';
alter role ${DBROLE} set default_transaction_isolation to 'read committed';
alter role ${DBROLE} set timezone to 'UTC';
SQL

# create the database(es)
echo "==> Creating database: ${DBNAME}"
PGPASSWORD="${POSTGRES_PASSWORD}" psql ${SELECT_DATABASE} -p ${DBPORT} -U ${POSTGRES_USER} postgres <<SQL
create database ${DBNAME} with owner ${DBROLE};
grant all privileges on database ${DBNAME} to ${DBROLE};
SQL
