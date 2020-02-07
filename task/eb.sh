#!/bin/bash
# shellcheck disable=SC2164
# shellcheck disable=SC2124
# shellcheck disable=SC2034
# shellcheck disable=SC2086

if [ -z "$WDIR" ]; then
  echo "[ERROR] env var WDIR can not be EMPTY"
  exit 1
fi

if [ ! -d "$WDIR" ]; then
  echo "[ERROR] task/$WDIR do not exist"
  exit 2
fi

# source common functions
. common.sh

function set_eb_env() {
  # check env
  echo "[INFO] env get status..."
  if ! (eb status); then
    envList=$(eb list)
    echo "[INFO] env not set, setting ${envList[0]}"
    eb use ${envList[0]}
    echo "[INFO] env get status..."
    eb status
  fi
}

function upload_env() {
  local ENV_HASHMAP
  local ENV_STRING=""
  declare -A ENV_HASHMAP
  read_files_to_hashmap ENV_HASHMAP ".env" ".env.aws"
  # declare -p ENV_HASHMAP # check hashmap content
  hashmap_to_string ENV_HASHMAP ENV_STRING

  echo "[INFO] will set env variables..."
  for pair in $ENV_STRING; do
    echo "     | $pair"
  done
  echo "[INFO] update begin..."
  eb setenv $ENV_STRING
  echo "[INFO] update done."
}

cd "$WDIR"
echo "#####################################################################"
echo "##### [INFO] Executing ElasticBeanstalk from inside '$WDIR' directory"
echo "#####################################################################"

ARGIN="$@"
set_eb_env

if [[ "$ARGIN" == 'repenv' ]]; then
  upload_env
else
  eb "$ARGIN"
fi
