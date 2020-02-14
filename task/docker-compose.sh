#!/usr/bin/env bash

# shellcheck disable=SC2086
# shellcheck disable=SC2124
# shellcheck disable=SC2164

. common.sh


echo "###################################################################"
echo "##### [INFO] Executing docker-compose from inside '$WDIR' directory"
echo "###################################################################"
check_wdir
symlink_dev_files
cd "$WDIR"
reload_env  ".env.dc" \
            "../../.envfiles/*"

ARGINPUT="$@"
CONFIG_YAMLS="
-f docker-compose.yml
-f docker-compose.override.yml
-f docker-compose.limits.yml
"

docker-compose $CONFIG_YAMLS $ARGINPUT