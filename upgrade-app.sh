#!/bin/sh
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
cmd ./make_env.py docker.env
if [[ ! -f .latest -o $(find . -mtime +48h -name .latest) ]]; then
   docker tag ${APP_NAME}:latest ${APP_NAME}:previous
   cmd touch .latest
fi 
cmd docker-compose build app
cmd docker-compose down
cmd docker-compose up -d app

