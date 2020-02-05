#!/bin/bash

DC_VER_CUR="$(docker-compose --version)"
DC_VER_NEW=1.25.4

if [[ "$DC_VER_NEW" != *"$DC_VER_CUR"* ]]; then
  echo "[INFO] Docker-compose installing"
  if [ -f "/usr/local/bin/docker-compose" ]; then
    sudo rm /usr/local/bin/docker-compose
  fi
  DC_URL=https://github.com/docker/compose/releases/download
  DC_URL=$DC_URL/$DC_VER_NEW/docker-compose-$(uname -s)-$(uname -m)
  sudo curl -L $DC_URL -o /usr/local/bin/docker-compose
  if [ $? -eq 0 ]; then
    sudo chmod +x /usr/local/bin/docker-compose
    docker-compose --version
  fi
fi
