#!/bin/bash


if [ -z "$WDIR" ]; then
  echo "[ERROR] env var WDIR can not be EMPTY"
  exit 1
fi

if [ ! -d "$WDIR" ]; then
  echo "[ERROR] task/$WDIR do not exist"
  exit 2
fi


# shellcheck disable=SC2164
cd "$WDIR"
echo "#####################################################################"
echo "##### [INFO] Executing ElasticBeanstalk from inside '$WDIR' directory"
echo "#####################################################################"

# shellcheck disable=SC2124
ARGIN="$@"

function string_to_hashmap() {
  local CHAR='='

  local array=( $1 )
  local -n _hashmap=$2 # use nameref for indirection
  for x in "${array[@]}" ; do
     KEY="${x%%${CHAR}*}"
     VALUE="${x##*${CHAR}}"
     _hashmap["$KEY"]="$VALUE"
  done

}

function hashmap_to_string() {
  local CHAR='='
  local -n _hashmap=$1 # use nameref for indirection
  local -n _string=$2

  local KEYS=${!_hashmap[@]}

  KEYS=$(echo $KEYS | tr ' ' '\n' | sort | tr '\n' ' ')

  local array=( )
  local pair
  for key in $KEYS; do
    pair=("$key=${_hashmap[$key]}")
    array+=( $pair )
#    echo "$pair"
  done

  _string="${array[@]}"
}

function upload_env() {

  declare -A ENV_HASHMAP
  declare -A ENV_STRING
  DOCKER_ENV="$(cat .env)"
  AWS_EB_ENV="$(cat .env.aws)"
  string_to_hashmap "$DOCKER_ENV" ENV_HASHMAP
  string_to_hashmap "$AWS_EB_ENV" ENV_HASHMAP
  hashmap_to_string ENV_HASHMAP ENV_STRING
  # declare -p ENV_HASHMAP # check hashmap content
  # shellcheck disable=SC2086
  echo "[INFO] Update env for..."
  eb status
  echo "[INFO] with variables..."
  for pair in $ENV_STRING; do
    echo "     | $pair"
  done
  echo "[INFO] update begin..."
  eb setenv $ENV_STRING
  echo "[INFO] update done."
}

if [[ "$ARGIN" == 'repenv' ]]; then
  upload_env
else
  eb "$ARGIN"
fi


