#!/bin/sh
source .env || exit 1
cd media
find . -type f | sed -e 's/^\.\///' | xargs -I@ s3cmd -c ../.s3cfg put --acl-public --guess-mime-type "@" "s3://${S3_API_BUCKET}/@"

