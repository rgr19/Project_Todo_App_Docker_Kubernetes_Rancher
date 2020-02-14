#!/bin/bash

echo "[INFO] Source 'common.sh' in DIR $PWD"

PROD="prod"
DEV="dev"

function datetime() {
  date "+%Y%m%d-%H%M%S"
}

function string_to_hashmap() {
  local CHAR='='
  if [[ "$#" != "2" ]]; then
    echo "[ERROR] Wrong number of arguments $#/2"
    exit 1
  fi

  local array=($1)
  local -n _hashmap=$2 # use nameref for indirection
  for x in "${array[@]}"; do
    KEY="${x%%${CHAR}*}"
    VALUE="${x##*${CHAR}}"
    _hashmap["$KEY"]="$VALUE"
  done

}

function read_files_to_hashmap() {

  if [[ $# -lt 2 ]]; then
    echo "[ERROR] Wrong number of arguments: $# < 2"
    exit 1
  fi

  local -n hashmap=$1
  shift
  local filesList="$@"
  local fileContent=""
  local fileName=""
  for filePath in $filesList; do
    fileContent="$(cat $filePath)"
    string_to_hashmap "$fileContent" hashmap
  done

}

function hashmap_to_string() {

  if [[ "$#" != "2" ]]; then
    echo "[ERROR] Wrong number of arguments $#/2"
    exit 1
  fi

  local CHAR='='
  local -n _hashmap=$1 # use nameref for indirection
  local -n _string=$2

  local KEYS=${!_hashmap[@]}

  KEYS=$(echo $KEYS | tr ' ' '\n' | sort | tr '\n' ' ')

  local array=()
  local pair
  for key in $KEYS; do
    pair=("$key=${_hashmap[$key]}")
    array+=($pair)
    #    echo "$pair"
  done

  _string="${array[@]}"
}

function read_dir_to_hashmap() {

  local -n _hashmap=$1
  shift
  local dirList=$@

  for d in $dirList; do
    _hashmap["$(basename $d)"]="$(cat $d)"
  done
}

function read_env_variables() {
  local ENV_HASHMAP
  local -n _ENV_STRING="$1"
  local ENV_FILES="$2"
  local ENV_DIRS="$3"
  declare -A ENV_HASHMAP
  read_files_to_hashmap ENV_HASHMAP $ENV_FILES
  read_dir_to_hashmap ENV_HASHMAP $ENV_DIRS
  # declare -p ENV_HASHMAP # check hashmap content
  hashmap_to_string ENV_HASHMAP _ENV_STRING
}

function get_github_branch_current() {
  git rev-parse --abbrev-ref HEAD
}

function get_git_user_name() {
  git config user.name
}

function check_wdir() {
  if [ -z "$WDIR" ]; then
    echo "[ERROR] env var WDIR can not be EMPTY"
    exit 1
  fi

  if [ ! -d "$WDIR" ]; then
    echo "[ERROR] task/$WDIR do not exist"
    exit 2
  fi

}

function symlink_files() {
  local src="$1"
  shift
  local files="$@"

  echo "[INFO] Linking files:"
  for f in $files; do
    local DEST="$WDIR/$f"
    local SRC="../$src/$f"
    if [ ! -f "$DEST" ]; then
      if [ ! -L "$DEST" ]; then
        echo "     | link from $SRC to $DEST"
        ln -s $SRC $DEST
      fi
    fi

  done
}

function symlink_files_from_src() {
  local SRC="$1"
  local PREFIX="$2"
  local SUFFIX="$3"

  echo "[INFO] Linking files:"
  for d in "$PREFIX"*"$SUFFIX"; do
    target="$WDIR/$(basename $d)"
    if [ ! -f "$target" ]; then
      if [ ! -L "$target" ]; then
        local SRC="../$d"
        local DEST="$target"
        echo "     | link from $SRC to $DEST"
        ln -s $SRC $DEST
      fi
    fi
  done
}

function symlink_prod_files() {
  files=".env.dc docker-compose.override.yml docker-compose.limits.yml"
  symlink_files $PROD $files
  symlink_files_from_src "$PROD" 'docker' '.sh'

}

function symlink_dev_files() {
  files="docker-compose.yml"
  symlink_files "$DEV" $files
  symlink_files_from_src "$DEV" 'docker' '.sh'

}

function guess_build_type() {
  local -n _BUILD_TYPE=$1
  local WDIR=$2

  if [[ $# -ne 2 ]]; then
    echo "[ERROR] Wrong number of arguments $#/1"
    exit 1
  fi

  if [[ "$WDIR" == *'dev'* ]]; then
    _BUILD_TYPE='dev'
  else
    _BUILD_TYPE='prod'
  fi

}

function reload_env() {

  if [ "$#" -lt "1" ]; then
    echo "[ERROR] Wrong number of arguments $# < 1"
    exit 1
  fi

  local ENV_STRING=""
  local ENV_FILES="$1"
  local ENV_DIRS="$2"
  local BUILD_TYPE=""
  read_env_variables ENV_STRING "$ENV_FILES" "$ENV_DIRS" #".envfiles.dc" "../../.envfiles/*"
  guess_build_type BUILD_TYPE $WDIR

  ENV_STRING="BUILD_TYPE=$BUILD_TYPE $ENV_STRING"

  echo "[INFO] set env variables..."
  echo "" >".env"
  for pair in $ENV_STRING; do
    echo "     | $pair"
    echo "$pair" >>".env"
  done
}
