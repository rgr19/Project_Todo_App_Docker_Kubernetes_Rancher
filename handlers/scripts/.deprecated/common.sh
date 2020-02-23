#!/bin/bash
# shellcheck disable=SC2124
# shellcheck disable=SC2086
# shellcheck disable=SC2206
# shellcheck disable=SC2206
# shellcheck disable=SC2206

function print_ntimes() {
  if [[ "$#" -lt 2 ]]; then
    echo "[ERROR: ${LINENO}] Wrong number of arguments ${#}/2"
    exit 1
  fi

  local CHAR="$1"
  shift
  local NTIMES="$@"

  python -c "print('$CHAR'*$NTIMES)"
}

K8S='k8s'
PROD="prod"
DEV="dev"
K8S_DIR='k8s'
DEV_DIR="docker_dev"
PROD_DIR="docker_prod"

BUILD_TYPE=""
RUNTIME_TYPE=""

function datetime() {
  date "+%Y%m%f-%H%M%S"
}

function get_github_branch_current() {
  git rev-parse --abbrev-ref HEAD
}

function get_git_user_name() {
  git config user.name
}

function check_project_env() {

  if [ -z "$CWD" ]; then
    echo "[ERROR: ${LINENO}] env var CWD can not be EMPTY"
    exit 1
  fi

  if [ ! -d "$CWD" ]; then
    echo "[ERROR: ${LINENO}] task/$CWD do not exist"
    exit 2
  fi

  if [ -z "$WDIR" ]; then
    echo "[ERROR: ${LINENO}] env var WDIR can not be EMPTY"
    exit 1
  fi

  if [ ! -d "$WDIR" ]; then
    echo "[ERROR: ${LINENO}] task/$WDIR do not exist"
    exit 2
  fi

}

function symlink_files_from_src() {
  local SRC="$1"
  shift
  local FILES="$@"
  local src
  local dest
  print_ntimes "#" 100

  echo "[INFO: ${LINENO}] Linking : FILES($FILES) SRC($SRC)"
  for f in $FILES; do
    src="../$SRC/$f"
    dest="$WDIR/$f"
    echo "     | link from $src to $dest"
    if [ ! -f "$dest" ]; then
      if [ ! -L "$dest" ]; then
        ln -s $src $dest
      fi
    fi

  done
}

function symlink_from_src_by_bothfix() {
  local SRC="$1"
  local PREFIX="$2"
  local SUFFIX="$3"
  local src
  local dest

  local FILES=("${SRC}/${PREFIX}"*"${SUFFIX}")
  print_ntimes "#" 100

  echo "[INFO: ${LINENO}] Linking : files SRC($SRC) PREFIX($PREFIX) SUFFIX($SUFFIX):"
  for f in $FILES; do
    src="../$f"
    dest="$WDIR/$(basename $f)"
    echo "     | link from $src to $dest"
    if [ ! -f "$dest" ]; then
      if [ ! -L "$dest" ]; then
        ln -s $src $dest
      fi
    fi
  done
}

function symlink_k8s_files() {
  files=".env.k8s "
  symlink_files_from_src $K8S_DIR $files
}

function symlink_prod_files() {
  files=".env.dc docker-compose.override.yml docker-compose.limits.yml"
  symlink_files_from_src $PROD_DIR $files
  symlink_from_src_by_bothfix "$PROD_DIR" 'docker' '.sh'
}

function symlink_dev_files() {
  files="docker-compose.yml"
  symlink_files_from_src "$DEV_DIR" $files
  symlink_from_src_by_bothfix "$DEV_DIR" 'docker' '.sh'

}

function guess_and_save_build_type() {
  local -n _BUILD_TYPE=$1
  local WDIR=$2

  if [[ $# -ne 2 ]]; then
    echo "[ERROR: ${LINENO}] Wrong number of arguments $#/1"
    exit 1
  fi
  print_ntimes "#" 100
  echo "[INFO: ${LINENO}] Guess BUILD_TYPE used to select Dockerfile.BUILD_TYPE for building images:"
  if [[ "$WDIR" == "$DEV_DIR" ]]; then
    _BUILD_TYPE=$(tr $DEV)
  else
    _BUILD_TYPE=$PROD
  fi
  echo "     | $_BUILD_TYPE"

  echo "$_BUILD_TYPE" >$CWD/.envfiles/BUILD_TYPE
}

function guess_and_save_runtime_type() {
  local -n _RUNTIME_TYPE=$1
  local WDIR=$2

  if [[ $# -ne 2 ]]; then
    echo "[ERROR: ${LINENO}] Wrong number of arguments $#/1"
    exit 1
  fi
  print_ntimes "#" 100
  echo "[INFO: ${LINENO}] Guess RUNTIME_TYPE used to know where are we executing Todo App (local, docker, aws, k8s, kompose):"
  _RUNTIME_TYPE=$WDIR
  echo "     | $_RUNTIME_TYPE "

  echo "$_RUNTIME_TYPE" >$CWD/.envfiles/RUNTIME_TYPE

}

function string_to_hashmap() {
  local CHAR='='
  if [[ "$#" != "2" ]]; then
    echo "[ERROR: ${LINENO}] Wrong number of arguments $#/2"
    exit 1
  fi

  local array=($1)
  local -n _hashmap=$2 # use nameref for indirection
  for x in "${array[@]}"; do
    key="${x%%${CHAR}*}"
    value="${x##*${CHAR}}"
    _hashmap["${key}"]="$value"
  done

}

function hashmap_to_string() {

  if [[ "$#" != "2" ]]; then
    echo "[ERROR: ${LINENO}] Wrong number of arguments $#/2"
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
    pair=("${key}=${_hashmap[$key]}")
    array+=($pair)
    #    echo "$pair"
  done

  _string="${array[@]}"
}

function read_env_files_to_hashmap() {

  if [[ $# -lt 2 ]]; then
    echo "[ERROR: ${LINENO}] Wrong number of arguments: $# < 2"
    exit 1
  fi

  local -n hashmap=$1
  shift 1
  local filesList="$@"
  local fileContent=""
  local filePath=""

  for filePath in $filesList; do
    fileContent="$(cat $filePath | grep -v "#")"
    string_to_hashmap "$fileContent" hashmap
  done

}

function read_global_dir_to_hashmap() {

  local -n _hashmap=$1
  shift 1
  local dirList=$@

  for f in $dirList; do
    _hashmap["$(basename $f)"]="$(cat $f | grep -v "#")"
  done
}

function read_env_variables() {
  local -n _ENV_STRING="$1"
  local ENV_FILES="$2"
  local ENV_DIRS="$3"
  local ENV_HASHMAP
  declare -A ENV_HASHMAP
  if [ -n "$ENV_FILES" ]; then
    read_env_files_to_hashmap ENV_HASHMAP $ENV_FILES
  fi
  if [ -n "$ENV_DIRS" ]; then
    read_global_dir_to_hashmap ENV_HASHMAP $ENV_DIRS
  fi
  # declare -p ENV_HASHMAP # check hashmap content
  hashmap_to_string ENV_HASHMAP _ENV_STRING
}


function reload_env() {

  if [ "$#" -lt "2" ]; then
    echo "[ERROR: ${LINENO}] Wrong number of arguments $# != 2"
    echo "      | Required:  ENV_FILES, ENV_DIRS"
    exit 1
  fi


  local ENV_STRING=""
  local ENV_FILES="$1"
  local ENV_DIRS="$2/"*
  read_env_variables ENV_STRING "$ENV_FILES" "$ENV_DIRS"

  print_ntimes "#" 100
  echo "[INFO: ${LINENO}] set env variables..."
  echo "" >".env"
  for pair in $ENV_STRING; do
    echo "     | $pair"
    echo "$pair" >>".env"
  done
}

function template_substitute_env_vars() {
  echo "$@"
  $(which python3) $CWD/scripts/file_expand_vars_from_envfile.py "$@"
}

function reload_nested_env() {

  if [[ "$#" -ne 2 ]]; then
    echo "[ERROR: ${LINENO}] Wrong number of arguments ${#}/2"
    exit 1
  fi

  local ENV_SRC=$1
  local ENV_TARGET=$2

  if [ -f "$ENV_TARGET" ]; then
    mv "$ENV_TARGET" "$ENV_TARGET.nested"
  fi

  template_substitute_env_vars \
    "$ENV_SRC" \
    "$ENV_TARGET.nested" \
    "$ENV_TARGET"

  rm "$ENV_TARGET.nested"

}

function loop_curl_and_block() {
  local TARGETS="$@"
  print_ntimes "#" 100
  echo "[INFO: ${LINENO}] Loop and send request to TARGETS: "
  set +e
  while true; do
    for target in $TARGETS; do
      print_ntimes "=" 100
      echo " >>> | curl $target"
      print_ntimes "-" 100
      curl -kL $target
    done
    print_ntimes "=" 100
    read -p "[PAUSE] Press ENTER to continue loop, CTRL+C to stop."
  done
  set -e
}

function expand_template_yamls() {
  print_ntimes "#" 100
  # expand env variables into template and save to Dockerrun.aws.json
  echo "[INFO: ${LINENO}] : Expand env variables in YAML templates:"

  local SRC_DIR="$1"
  local DEST_DIR="$2"

  files=$(find $SRC_DIR | egrep ".yml|.yaml")
  for template in $files; do
    template_substitute_env_vars ".env $template $DEST_DIR/$(basename $template)"
  done

}

function convert_env_to_yaml() {
  print_ntimes "#" 100
  $(which python3) $CWD/scripts/convert_env_to_yaml.py "$@"

}

print_ntimes "#" 100
echo "[INFO: ${LINENO}] Source 'common.sh' in DIR $PWD"
guess_and_save_build_type BUILD_TYPE $WDIR
guess_and_save_runtime_type RUNTIME_TYPE $WDIR
