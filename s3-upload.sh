#!/bin/sh
source .env || exit 1
bucket="ywfa-7b89f69-bf3e-446f-a851-c4ed5be3d6d1"
cd media
find . -type f | sed -e 's/^\.\///' | xargs -I@ s3cmd put --acl-public --guess-mime-type "@" "s3://${bucket}/@"