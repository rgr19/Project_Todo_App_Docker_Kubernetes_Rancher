#!/usr/bin/env bash


# shellcheck disable=SC2164
cd ../../src
npm -g list recursive-install -q
if [ $? -ne 0 ]; then
  sudo npm i -g recursive-install -q
fi

npm-recursive-install -q
