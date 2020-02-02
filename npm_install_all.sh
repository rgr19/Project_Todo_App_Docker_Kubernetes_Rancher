#!/usr/bin/env bash

DIRS="$(find $PWD -maxdepth 2 -name package.json -type f)"

CWD=$PWD

FAILURES_FILE=$CWD/npm_install_failed.txt
SUCCESS_FILE=$CWD/npm_install_success.txt

touch $FAILURES_FILE
touch $SUCCESS_FILE

FAILURES_ARRAY=()

for d in $DIRS; do
    echo "NPM INSTALL $d"
    if [ -d "$(dirname $d)" ]; then
      cd "$(dirname $d)"
    else
      echo "no such directory, skipping"
      continue
    fi
    grep -Fxq "$d" $SUCCESS_FILE
    if [ $? -ne 0 ]; then
      echo "not in success file"
      npm install --silent
      npm audit fix --silent
      if [ $? -ne 0 ]; then
        echo "installation failed"
        grep -Fxq "$d" $FAILURES_FILE
        FAILURES_ARRAY+=("$d")
      else
        echo "installation successful"
        echo "$d" >> $SUCCESS_FILE
      fi
    else
      echo "in success file, skipping"
    fi
    cd $CWD || true
done

echo "" > $FAILURES_FILE

for d in "${FAILURES_ARRAY[@]}"; do
  echo "$d" >> $FAILURES_FILE
done
