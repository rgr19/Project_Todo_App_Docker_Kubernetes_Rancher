#!/usr/bin/env bash

# shellcheck disable=SC2164

if [ -z "$WDIR" ]; then
  echo "[ERROR] env var WDIR can not be EMPTY"
  exit 1
fi

if [ ! -d "$WDIR" ]; then
  echo "[ERROR] task/$WDIR do not exist"
  exit 2
fi

if [ ! -f "$WDIR/docker-compose.yml" ]; then
  if [ ! -L "$WDIR/docker-compose.yml" ]; then
    ln -s "../dev/docker-compose.yml" "$WDIR/docker-compose.yml"
  fi
fi

for d in "dev/dc_"*; do
  target="$WDIR/$(basename $d)"
  if [ ! -f "$target" ]; then
    if [ ! -L "$target" ]; then
      ln -s "../dev/$d" "$target"
    fi
  fi
done

. common.sh

function guess_build_type() {

  if [[ "$WDIR" == *'dev'* ]]; then
    BUILD_TYPE='dev'
  elif [[ "$WDIR" == *'prod'* ]]; then
    BUILD_TYPE='prod'
  fi

}

function reload_env() {
  local ENV_STRING=""
  read_env_variables ENV_STRING ".env.dc" "../../.env/*"
  guess_build_type

  ENV_STRING="BUILD_TYPE=$BUILD_TYPE $ENV_STRING"

  echo "[INFO] set env variables..."
  echo "" > ".env"
  for pair in $ENV_STRING; do
    echo "     | $pair"
    echo "$pair" >>".env"
  done
}

cd "$WDIR"
echo "###################################################################"
echo "##### [INFO] Executing docker-compose from inside '$WDIR' directory"
echo "###################################################################"

reload_env
docker-compose "$@"
