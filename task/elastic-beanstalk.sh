#!/bin/bash
# shellcheck disable=SC2164
# shellcheck disable=SC2124
# shellcheck disable=SC2034
# shellcheck disable=SC2086



# source common functions
. common.sh

function set_eb_env() {
  # check env
  echo "[INFO] env get status..."
  if ! (eb status); then
    envList=$(eb list)
    if [ -z "$envList" ]; then
      echo "[ERROR] EB Env List is empty"
      exit 1
    fi
    echo "[INFO] env not set, setting ${envList[0]}"
    eb use ${envList[0]}
    echo "[INFO] env get status..."
    eb status
  fi
}


function upload_env() {
  local ENV_STRING=""
  local BUILD_TYPE=""

  read_env_variables ENV_STRING ".env.dc .env.aws" "../../.envfiles/*"
  guess_build_type BUILD_TYPE $WDIR

  ENV_STRING="BUILD_TYPE=$BUILD_TYPE $ENV_STRING"

  echo "[INFO] will set env variables..."
  for pair in $ENV_STRING; do
    echo "     | $pair"
  done
  echo "[INFO] update begin..."
  eb setenv $ENV_STRING
  echo "[INFO] update done."
}

echo "#####################################################################"
echo "##### [INFO] Executing ElasticBeanstalk from inside '$WDIR' directory"
echo "#####################################################################"
check_wdir
symlink_dev_files
symlink_prod_files
cd "$WDIR"
ARGIN="$@"
set_eb_env

if [[ "$ARGIN" == 'repenv' ]]; then
    upload_env
else
  eb "$ARGIN"
fi
