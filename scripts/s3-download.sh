#!/bin/sh
: ${DOTENV:=./.env}
[ -f ./.env ] && source ${DOTENV} || { echo "${DOTENV} does not exist!" && exit 1; }
cd media
s3cmd -c ../.s3cfg sync "s3://${S3_API_BUCKET}" .

