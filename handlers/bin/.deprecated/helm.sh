#!/usr/bin/env bash
# shellcheck disable=SC2068
# shellcheck disable=SC2096
# shellcheck disable=SC2086
# shellcheck disable=SC2164
# shellcheck disable=SC2199
set -e
. ../scripts/common.sh
. ../scripts/common.k8s.sh
. ../scripts/common.helm.sh

echo "###################################################################"
echo "##### [INFO] Executing HELM from inside '$WDIR' directory"
echo "###################################################################"

check_project_env

helm_reload_files_from_templates $@

#
#helm delete todo-app || true
#
#until helm install todo-app ./todo-app/ --debug --replace --dry-run >dry-run.yaml; do
#  sleep 3
#  clear
#done
#
#until helm install todo-app ./todo-app/ --debug --replace >install.yaml; do
#  sleep 3
#  clear
#done
#
#kubectl get pod -n todo-app-$($CWD/scripts/string_replace.py "." "-" $CHART_VERSION) -w

