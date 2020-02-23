#!/usr/bin/env bash

function helm_reload_files_from_templates() {
  echo "[INFO] BEGIN Helm reload files from templates:"

  (
    cd "$CWD/task/helm" || exit 1

    for config in ".todo-app/*.yaml"*; do
      ../scripts/SortYaml.py \
        $config \
        $config
    done

    echo "[INFO] Expand ENVVARS in .todo-app/values/static.yaml"
    ../scripts/file_expand_vars_from_envfile.py \
      ".todo-app/values/static.yaml" \
      ".todo-app/values/static.yaml" \
      ".temp/values.static.yaml"

    echo "[INFO] Expand ENVVARS in .todo-app/secrets/dynamic.yaml"
    ../scripts/file_expand_vars_from_envdir.py \
      "$CWD/.secretfiles" \
      ".todo-app/secrets/dynamic.yaml" \
      ".temp/secrets.dynamic.yaml"

    echo "[INFO] Expand ENVVARS in .temp/values/dynamic.yaml by DIR .envfiles"
    ../scripts/file_expand_vars_from_envdir.py \
      "$CWD/.envfiles" \
      ".todo-app/values/dynamic.yaml" \
      ".temp/values.dynamic.yaml"

    echo "[INFO] Expand ENVVARS in .todo-app/Chart.yaml"

    if [ "$#" -eq 1 ]; then
      CHART_VERSION="$1"
    else
      CHART_VERSION=0.0.0
    fi

    CHART_VERSION=$CHART_VERSION envsubst <".todo-app/Chart.yaml" >".temp/Chart.yaml"

    ../scripts/flatten_yaml.py .temp/values.dynamic.yaml .temp/values.dynamic.yaml
    ../scripts/flatten_yaml.py .temp/values.dynamic.yaml .temp/values.dynamic.yaml

    echo "[INFO] Concat temp YAMLs"
    ../scripts/yamls_concat.py \
      .temp/values.yaml \
      .temp/values.*.yaml

    ../scripts/yamls_concat.py \
      .temp/secrets.yaml \
      .temp/secrets.*.yaml

    cp .temp/secrets.yaml todo-app/secrets/secrets.yaml
    cp .temp/values.yaml todo-app/values.yaml
    cp .temp/Chart.yaml todo-app/Chart.yaml

    helm lint todo-app
    if [ $? -ne 0 ]; then
      exit $?
    fi

    helm template todo-app >template.yaml
    if [ $? -ne 0 ]; then
      exit $?
    fi
  )
  echo "[INFO] END Helm reload files from templates."

}
