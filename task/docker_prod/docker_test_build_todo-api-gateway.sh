#!/usr/bin/env bash

if [ -z "$REPO_USER" ]; then
  DOCKER_HUB_ID="$(cat ../../DOCKER_HUB_ID)"
fi

docker build ../../src/todo-api-gateway \
             -f ../../src/common/Dockerfile.nodejs.builds \
             -t ${REPO_USER}/todo-api-gateway:1.0
