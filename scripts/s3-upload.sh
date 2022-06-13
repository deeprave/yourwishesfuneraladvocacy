#!/bin/sh
: ${DOTENV:=./.env}
[ -f ./.env ] && source ${DOTENV} || { echo "${DOTENV} does not exist!" && exit 1; }
cd media
find . -type f | sed -e 's/^\.\///' | xargs -I@ s3cmd put --acl-public --guess-mime-type "@" "s3://${S3_API_BUCKET}/@"

