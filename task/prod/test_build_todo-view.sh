#!/usr/bin/env bash

if [ -z "$REPO_USER" ]; then
  DOCKER_HUB_ID="$(cat ../../DOCKER_HUB_ID)"
fi

docker build ../../src/todo-view \
             -f ../../src/todo-view/Dockerfile.builds \
             -t ${REPO_USER}/todo-view:1.0


