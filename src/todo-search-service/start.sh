#!/bin/bash

if [ -z "$IS_AWS_EB" ]; then
  while ! curl http://todo-elastic:9200; do sleep 1; done
fi

npm start
