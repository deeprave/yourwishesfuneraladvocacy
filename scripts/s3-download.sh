#!/bin/sh
[ ! -f '.env' ] && cd ..
source .env || exit 1
cd media
s3cmd -c ../.s3cfg sync "s3://${S3_API_BUCKET}" .

