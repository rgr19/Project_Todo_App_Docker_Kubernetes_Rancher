#!/usr/bin/env bash

# shellcheck disable=SC2164
# shellcheck disable=SC2068
# shellcheck disable=SC2086
. common.sh

echo "###################################################################"
echo "##### [INFO] Executing Kompose from inside '$WDIR' directory"
echo "###################################################################"
check_project_env
symlink_dev_files
symlink_prod_files
cd "$WDIR"
reload_env ".env.dc .env.kompose" "../../.envfiles/"*

exit 0

mkdir -p config

CONFIG_FILES="
  -f docker-compose.yaml
  -f docker-compose.override.yaml
  -f docker-compose.limits.yaml
  -f kompose.override.yaml
"

echo "[INFO] Group docker-compose config with subsituted env variables to one file."
docker-compose $CONFIG_FILES config > docker-compose.resolved.yaml

kompose convert \
  -f docker-compose.resolved.yaml \
  --replicas=2 --verbose --out config $@

touch config/todo-config.dynamic.yaml
touch config/todo-secret.yaml
touch config/todo-namespace.yaml

rm config/*-claim*-*.yaml
rm config/*-claim*-*.yaml

echo "[INFO] Created kompose files:"
for path in config/*; do
  echo "    | $path"
done

echo "[INFO] Create additional override files:"
for path in config/*; do
  PATTERN="persistentvolumeclaim.yaml"
  REPLACE="persistentvolume.yaml"
  if [[ "$path" == *"${PATTERN}" ]]; then
    TARGET="${path%%${PATTERN}*}${REPLACE}"
    newPath="config/$(basename ${TARGET})"
    echo "    | $newPath"
    if [ -f "$newPath" ]; then
      rm "$newPath"
    fi
    cp "$path" "$newPath"
  fi
done

echo "[WARN] Kompose converted files require additional overriding to use them. Do it in files at DIR 'override'."
