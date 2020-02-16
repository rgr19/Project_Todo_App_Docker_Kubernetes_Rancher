#!/bin/bash
# shellcheck disable=SC2124
# shellcheck disable=SC2086
# shellcheck disable=SC2206
# shellcheck disable=SC2206
# shellcheck disable=SC2206

function print_ntimes() {
  if [[ "$#" -lt 2 ]]; then
    echo "[ERROR] Wrong number of arguments ${#}/2"
    exit 1
  fi

  local CHAR="$1"
  shift
  local NTIMES="$@"

  python -c "print('$CHAR'*$NTIMES)"
}

PROD="PROD"
DEV="DEV"
DEV_DIR="docker_dev"
PROD_DIR="docker_prod"

function datetime() {
  date "+%Y%m%f-%H%M%S"
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
    fileContent="$(cat $filePath | grep -v "#")"
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

function check_project_env() {

  if [ -z "$CWD" ]; then
    echo "[ERROR] env var CWD can not be EMPTY"
    exit 1
  fi

  if [ ! -d "$CWD" ]; then
    echo "[ERROR] task/$CWD do not exist"
    exit 2
  fi

  if [ -z "$WDIR" ]; then
    echo "[ERROR] env var WDIR can not be EMPTY"
    exit 1
  fi

  if [ ! -d "$WDIR" ]; then
    echo "[ERROR] task/$WDIR do not exist"
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

  echo "[INFO] Linking : FILES($FILES) SRC($SRC)"
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

  echo "[INFO] Linking : files SRC($SRC) PREFIX($PREFIX) SUFFIX($SUFFIX):"
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

function guess_build_type() {
  local -n _BUILD_TYPE=$1
  local WDIR=$2

  if [[ $# -ne 2 ]]; then
    echo "[ERROR] Wrong number of arguments $#/1"
    exit 1
  fi
  print_ntimes "#" 100
  echo "[INFO] Guess BUILD_TYPE used to select Dockerfile.BUILD_TYPE for building images:"
  if [[ "$WDIR" == "$DEV_DIR" ]]; then
    _BUILD_TYPE=$DEV
  else
    _BUILD_TYPE=$PROD
  fi
  echo "     | $_BUILD_TYPE"

}

function guess_runtime_type() {
  local -n _RUNTIME_TYPE=$1
  local WDIR=$2

  if [[ $# -ne 2 ]]; then
    echo "[ERROR] Wrong number of arguments $#/1"
    exit 1
  fi
  print_ntimes "#" 100
  echo "[INFO] Guess RUNTIME_TYPE used to know where are we executing Todo App (local, docker, aws, k8s, kompose):"
  _RUNTIME_TYPE=$WDIR
  echo "     | $_RUNTIME_TYPE "

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
  local RUNTIME_TYPE=""
  read_env_variables ENV_STRING "$ENV_FILES" "$ENV_DIRS" #".envfiles.dc" "../../.envfiles/*"
  guess_build_type BUILD_TYPE $WDIR
  guess_runtime_type RUNTIME_TYPE $WDIR

  ENV_STRING="
    $ENV_STRING
    BUILD_TYPE=$BUILD_TYPE
    RUNTIME_TYPE=$RUNTIME_TYPE
  "
  print_ntimes "#" 100
  echo "[INFO] set env variables..."
  echo "" >".env"
  for pair in $ENV_STRING; do
    echo "     | $pair"
    echo "$pair" >>".env"
  done
}

function template_substitute_env_vars() {
  $CWD/scripts/template_substitute.py "$@"
}

function reload_nested_env() {

  if [[ "$#" -ne 2 ]]; then
    echo "[ERROR] Wrong number of arguments ${#}/2"
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
  echo "[INFO] Loop and send request to TARGETS: "
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
  echo "[INFO] : Expand env variables in YAML templates:"

  local SRC_DIR="$1"
  local DEST_DIR="$2"

  files=$(find $SRC_DIR | egrep ".yml|.yaml")
  for template in $files; do
    "$CWD/scripts/template_substitute.py" \
      ".env" \
      "$template" \
      "$DEST_DIR/$(basename $template)"
  done

}

print_ntimes "#" 100
echo "[INFO] Source 'common.sh' in DIR $PWD"
