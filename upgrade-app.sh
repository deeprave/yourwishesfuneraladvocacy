#!/bin/sh
alias dc=docker-compose

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
cmd ./make_env.py -o docker.env
cmd docker-compose build app
cmd docker-compose down
cmd docker-compose up -d app

