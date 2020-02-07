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

cd "$WDIR"
echo "###################################################################"
echo "##### [INFO] Executing docker-compose from inside '$WDIR' directory"
echo "###################################################################"
docker-compose "$@"
