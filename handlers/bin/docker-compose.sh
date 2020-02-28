#!/usr/bin/env bash

# shellcheck disable=SC2086
# shellcheck disable=SC2124
# shellcheck disable=SC2164
# shellcheck disable=SC2016
set -e

source scripts/common.sh
source scripts/common.helm.sh

echo "###################################################################"
echo "##### [INFO] Executing docker-compose from inside '$WDIR' directory"
echo "###################################################################"
check_project_env
cd "$WDIR"

function docker_compose_reload_files_from_templates() {
  (
    PROD_CONFIG_YAMLS="
docker-compose.yaml
docker-compose.override.yaml
"

    DEV_CONFIG_YAMLS="
docker-compose.yaml
docker-compose.limits.yaml
"

    if [[ "$WDIR" == *"dev"* ]]; then
      CONFIG_YAMLS=$DEV_CONFIG_YAMLS
    elif [[ "$WDIR" == *"prod"* ]]; then
      CONFIG_YAMLS=$PROD_CONFIG_YAMLS
    else
      echo "[ERROR:${LINENO}] Wrong docker-compose WDIR: $WDIR"
      exit 1
    fi

    echo "[INFO] Helmchart todo-app values.yaml to .env for Docker-Compose"
    $CWD/taskset/scripts/convert_yaml_to_env.py \
      $CWD/taskset/helm/todo-app/values.yaml \
      ".env"

    $CWD/taskset/scripts/file_replace_string.py \
      ".env" \
      ".env" \
      "Mi Gi" \
      "m g"

    WITH_MEM_LIMITS="true"

    if [ "$WITH_MEM_LIMITS" == "true" ]; then
      export VARS_DOCKER_COMPOSE_VERSION=2.2
    else
      export VARS_DOCKER_COMPOSE_VERSION=3.7
    fi

    for yml in $CONFIG_YAMLS; do
      echo "[INFO] Expand ENVVARS in copy of template: $yml"
      $CWD/taskset/scripts/file_expand_vars_from_envfile.py ".env" "../template/$yml" "$yml"
    done

    for yml in $CONFIG_YAMLS; do
      echo "[INFO] Expand VARS_DOCKER_COMPOSE_VERSION in : $yml"

      $CWD/taskset/scripts/file_replace_string.py \
        "$yml" \
        "$yml" \
        "VARS_DOCKER_COMPOSE_VERSION" \
        "${VARS_DOCKER_COMPOSE_VERSION}"

      # ERROR: causes to expand unknown variables to empty strings
      #      temp="$(VARS_DOCKER_COMPOSE_VERSION=2.2 envsubst <$yml)"
      #      echo "$temp" >"$yml"
    done
  )
}

ARGINPUT="$@"
if [[ "$ARGINPUT" == *"up"* ]] || [[ "$ARGINPUT" == *"build"* ]]; then
  helm_reload_files_from_templates
  docker_compose_reload_files_from_templates
fi

F_CONFIG_YAMLS=""
for yml in $CONFIG_YAMLS; do
  F_CONFIG_YAMLS="-f $yml $F_CONFIG_YAMLS"
done

docker-compose $F_CONFIG_YAMLS $ARGINPUT
