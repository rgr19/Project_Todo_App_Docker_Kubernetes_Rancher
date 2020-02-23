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

function guess_and_save_build_type() {
  local _BUILD_TYPE=""
  local WDIR=$1

  if [[ $# -ne 1 ]]; then
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
  local _RUNTIME_TYPE=""
  local WDIR=$1

  if [[ $# -ne 1 ]]; then
    echo "[ERROR: ${LINENO}] Wrong number of arguments $#/1"
    exit 1
  fi
  print_ntimes "#" 100
  echo "[INFO: ${LINENO}] Guess RUNTIME_TYPE used to know where are we executing Todo App (local, docker, aws, k8s, kompose):"
  _RUNTIME_TYPE=$WDIR
  echo "     | $_RUNTIME_TYPE "

  echo "$_RUNTIME_TYPE" >$CWD/.envfiles/RUNTIME_TYPE

}

K8S='k8s'
PROD="prod"
DEV="dev"
K8S_DIR='k8s'
DEV_DIR="docker_dev"
PROD_DIR="docker_prod"

BUILD_TYPE=""
RUNTIME_TYPE=""

print_ntimes "#" 100
echo "[INFO: ${LINENO}] Source 'common.sh' in DIR $PWD"
guess_and_save_build_type $WDIR
guess_and_save_runtime_type $WDIR
