#!/usr/bin/env bash

# docker-compose [-f <arg>...] [options] [COMMAND] [ARGS...]
# docker-compose -f ../common/docker-compose.yml -f docker-compose.override.yml up --build -d
docker-compose  up --build -d
