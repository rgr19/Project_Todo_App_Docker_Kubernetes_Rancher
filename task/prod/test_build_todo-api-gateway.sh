#!/usr/bin/env bash

if [ -z "$REPO_USER" ]; then
  REPO_USER="$(cat ../../REPO_USER)"
fi

docker build ../../src/todo-api-gateway \
             -f ../../src/common/Dockerfile.nodejs.prod \
             -t ${REPO_USER}/todo-api-gateway:1.0
