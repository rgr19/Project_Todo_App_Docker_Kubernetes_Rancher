#!/usr/bin/env bash

if [ -z "$REPO_USER" ]; then
  REPO_USER="$(cat ../../REPO_USER)"
fi

docker build ../../src/todo-view \
             -f ../../src/todo-view/Dockerfile.builds \
             -t ${REPO_USER}/todo-view:1.0


