#!/bin/sh
source ./.env
cd media
s3cmd -c ../.s3cfg sync "s3://${S3_API_BUCKET}" .
