#!/bin/bash -xe

echo "[INFO] Source 'common.sh'."

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

  if [[ $# -le 2 ]]; then
    echo "[ERROR] Wrong number of arguments: $# <= 2"
    exit 1
  fi

  local -n hashmap=$1
  shift
  local filesList="$@"
  local fileContent=""
  local fileName=""
  for fileName in $filesList; do
    fileContent="$(cat $fileName)"
    echo $fileContent
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

function get_github_branch_current() {
  git rev-parse --abbrev-ref HEAD
}

function get_git_user_name() {
  git config user.name
}