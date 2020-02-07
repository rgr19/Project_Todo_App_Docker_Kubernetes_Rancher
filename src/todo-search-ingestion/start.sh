#!/bin/bash

if [ -z "$IS_AWS_EB" ]; then
  while ! curl http://todo-elastic:9200; do sleep 1; done
fi

while ! curl http://todo:todo1234@todo-rabbitmq:15672/api/aliveness-test/%2F; do sleep 1; done

npm start
