#!/bin/bash
APP_NAME=ywfa

cmd () {
  args="$@"
  command=${1}
  echo '===>' ${args}
  ${args} || { echo "${command}" exited with status "${?}"; exit $?; }
  echo ""
}

cmd git fetch -atpf
cmd git checkout master
cmd git pull
cmd scripts/sup.py build docker.env
if [[ ! -f .latest || $(find . -mtime +24 -name .latest) ]]; then
   docker tag ${APP_NAME}:latest ${APP_NAME}:previous
   cmd touch .latest
fi 
cmd docker-compose build app
cmd docker-compose down
cmd docker-compose up -d app

