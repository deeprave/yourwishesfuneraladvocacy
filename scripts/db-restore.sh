#!/usr/bin/env bash
: ${DOTENV:=./.env}
[ -f ./.env ] && source ${DOTENV} || { echo "${DOTENV} does not exist!" && exit 1; }
[[ ! -z $DBHOST ]] && SELECT_DATABASE=${SELECT_DATABASE:-"-h ${DBHOST}"}

RESTORE_SQL=backups/restore.sql

# populate the database(es)
echo "==> Populate database: ${DBNAME}"
PGPASSWORD="${DBPASS}" psql ${SELECT_DATABASE} -p ${DBPORT} -U ${DBUSER} $DBNAME < $RESTORE_SQL
