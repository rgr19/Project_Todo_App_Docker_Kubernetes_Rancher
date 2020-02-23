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
      echo "[ERROR] EB Env List is empty. Go to AWS web and create App and then App/Env in ElasticBeanstalk."
      exit 1
    fi
    echo "[INFO] env not set, setting ${envList[0]}"
    eb use ${envList[0]}
    echo "[INFO] env get status..."
    eb status
  fi
}


function upload_env() {
  ENV_STRING="$(cat .env)"

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
check_project_env
symlink_dev_files
symlink_prod_files
cd "$WDIR"
reload_env ".env.dc .env.aws" "../../.envfiles/"*
# expand env variables into template and save to Dockerrun.aws.json
template_substitute_env_vars \
    ".env" \
    "template/Dockerrun.aws_template.json" \
    "$CWD/Dockerrun.aws.json"

ARGIN="$@"
set_eb_env
if [[ "$ARGIN" == 'UPLOAD_ENV' ]]; then
  upload_env
else
  eb "$ARGIN"
fi

