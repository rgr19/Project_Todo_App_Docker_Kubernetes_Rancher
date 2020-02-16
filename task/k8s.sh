#!/usr/bin/env bash
# shellcheck disable=SC2068
# shellcheck disable=SC2096
# shellcheck disable=SC2086
# shellcheck disable=SC2164
# shellcheck disable=SC2199
set -e
. common.sh
. common.k8s.sh

function parse_arginput_tasks() {
  MODE="NONE"
  if [ "$#" -gt 0 ]; then
    if [[ "$@" == "MODE"* ]]; then
      shift
      MODE="$@"
    fi
  fi
}

echo "###################################################################"
echo "##### [INFO] Executing K8S from inside '$WDIR' directory"
echo "###################################################################"
parse_arginput_tasks $@
check_project_env
symlink_dev_files
symlink_prod_files
cd "$WDIR"
reload_env ".env.dc .env.k8s" "../../.envfiles/"*
reload_nested_env ".env.dc" ".env"

expand_template_yamls "template" "config"

CONFIG_YAMLS="
todo-namespace.yaml
todo-configmap.yaml
todo-secret.yaml
"

PV_YAMLS="
elastic-data-persistentvolume.yaml
elastic-data-persistentvolumeclaim.yaml
"

PVC_YAMLS="
postgres-data-persistentvolume.yaml
postgres-data-persistentvolumeclaim.yaml
"

DEPLOYMENT_STATEFUL_YAMLS="
todo-redis-deployment.yaml
todo-redis-service.yaml

todo-postgres-deployment.yaml
todo-postgres-service.yaml

todo-elastic-deployment.yaml
todo-elastic-service.yaml
"

DEPLOYMENT_TODO_SERVICES_YAMLS="
todo-cache-service-deployment.yaml
todo-cache-service-service.yaml

todo-storage-service-deployment.yaml
todo-storage-service-service.yaml

todo-search-service-deployment.yaml
todo-search-service-service.yaml
"

DEPLOYMENT_RABBITMQ_YAMLS="
todo-rabbitmq-deployment.yaml
todo-rabbitmq-service.yaml
todo-rabbitmq-management-service.yaml
"

DEPLOYMENT_INGESTION_YAMLS="
todo-cache-ingestion-deployment.yaml
todo-storage-ingestion-deployment.yaml
todo-search-ingestion-deployment.yaml

todo-api-gateway-deployment.yaml
todo-api-gateway-service.yaml
"

DEPLOYMENT_VIEW_YAMLS="
todo-view-deployment.yaml
todo-view-service.yaml
"

DEPLOYMENT_PROXY_YAMLS="
todo-proxy-deployment.yaml
todo-proxy-service.yaml
"

INGRESS="
todo-ingress.yaml
"

if [[ "$MODE" == *"FRESH"* ]]; then
  print_ntimes "#" 100
  echo "[INFO] FRESH: delete NAMESPACE todo, delete PVs:"
  kubectl delete namespace todo
  kubectl delete pv elastic-data-pv
  kubectl delete pv postgres-data-pv
fi

kubectl_apply_config $CONFIG_YAMLS
kubectl_apply_pv_pvc $PV_YAMLS $PVC_YAMLS
kubectl_apply_pods $DEPLOYMENT_STATEFUL_YAMLS
kubectl_apply_pods $DEPLOYMENT_TODO_SERVICES_YAMLS
kubectl_apply_pods $DEPLOYMENT_RABBITMQ_YAMLS
kubectl_apply_pods $DEPLOYMENT_INGESTION_YAMLS
kubectl_apply_pods $DEPLOYMENT_VIEW_YAMLS
kubectl_apply_pods $DEPLOYMENT_PROXY_YAMLS
kubectl_apply_svc $INGRESS

if [[ "$MODE" == *"VV"* ]]; then

  kubectl_describe_configmap
  kubectl_get_pv
  kubectl_get_pvc
  kubectl_get_svc

  if [[ "$MODE" == *"VVV"* ]]; then

    DEPLOYMENTS_AND_SERVICES="
    todo-redis
    todo-postgres
    todo-elastic
    todo-cache-service
    todo-storage-service
    todo-search-service
    todo-rabbitmq
    todo-api-gateway
    todo-proxy
    todo-view
    "

    DEPLOYMENTS="
    todo-cache-ingestion
    todo-storage-ingestion
    todo-search-ingestion
    "

    SERVICES="
    todo-rabbitmq-management
    "

    kubectl_describe_list_deploy_svc $DEPLOYMENTS_AND_SERVICES
    kubectl_describe_list_deploy $DEPLOYMENTS
    kubectl_describe_list_svc $SERVICES

  fi
  kubectl_get_pods_info
  kubectl_get_pods_list_logs

fi

if [[ "$MODE" == *"V"* ]]; then
  kubectl_watch_pods_svc_deploy
fi

CURL_TARGETS="
http://localhost:8080
http://127.0.0.1/8080
http://127.0.0.1/80
"

loop_curl_and_block $CURL_TARGETS
