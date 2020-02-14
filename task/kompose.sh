#!/usr/bin/env bash

# shellcheck disable=SC2164
# shellcheck disable=SC2068
# shellcheck disable=SC2086
. common.sh

echo "###################################################################"
echo "##### [INFO] Executing Kompose from inside '$WDIR' directory"
echo "###################################################################"
check_wdir
symlink_dev_files
symlink_prod_files
cd "$WDIR"
reload_env ".env.dc .env.k8s" "../../.envfiles/*"

mkdir -p converted

kompose convert \
  -f docker-compose.yml \
  -f docker-compose.override.yml \
  -f docker-compose.limits.yml \
  -f kompose.override.yml \
  --replicas=2 --verbose --out converted $@

echo "[INFO] Created kompose files:"
for path in converted/*; do
  echo "    | $path"
done

if [ -f "override/lock" ]; then
  echo "[WARN] Override dir LOCKED by 'override/lock'. Will not modify override."
else
  echo "[INFO] Backup kompose override files:"
  mkdir -p "override.bkp"
  if [ -d "override" ]; then
    BKP="override.bkp/$(datetime)"
    echo "     | Move 'override' to : $BKP"
    mv "override" $BKP
  fi
  mkdir -p "override"

  echo "[INFO] Create additional override files:"
  for path in converted/*; do
    PATTERN="persistentvolumeclaim.yaml"
    REPLACE="persistentvolume.yaml"
    if [[ "$path" == *"${PATTERN}" ]]; then
      TARGET="${path%%${PATTERN}*}${REPLACE}"
      newPath="override/$(basename ${TARGET})"
      echo "    | $newPath"
      if [ -f "$newPath" ]; then
        rm "$newPath"
      fi
      cp "$path" "$newPath"
    fi
  done

  echo "[INFO] Please edit override files for kompose:"
  for path in converted/*; do
    newPath="override/$(basename $path)"
    echo "    | $newPath"
    if [ -f "$newPath" ]; then
      rm "$newPath"
    fi
    cp "$path" "$newPath"
  done
fi
echo "[WARN] Kompose converted files require additional overriding to use them. Do it in files at DIR 'override'."
