#!/bin/bash

echo "[INFO] Source 'common.k8s.sh' in DIR $PWD"



function kubectl_watch_svc() {
  set +e
  echo "[INFO] GET Services in watch mode. CTRL+C to continue."
  kubectl get svc -w --namespace todo
  print_ntimes "#" 100
  set -e

}

function kubect_watch_pods() {
  set +e
  print_ntimes "#" 100
  echo "[INFO] GET Pods in watch mode. CTRL+C to continue."
  kubectl get pods -w --namespace todo
  print_ntimes "#" 100
  set -e
}

function kubect_watch_deploy() {
  set +e
  print_ntimes "#" 100
  echo "[INFO] GET Deployments in watch mode. CTRL+C to continue."
  kubectl get deploy -w --namespace todo
  set -e

}

function kubectl_watch_pods_svc_deploy() {
  kubectl_watch_svc
  kubect_watch_deploy
  kubect_watch_pods
}

function kubectl_watch_pv() {
  set +e
  print_ntimes "#" 100
  echo "[INFO] GET PV in watch mode. CTRL+C to continue."
  kubectl get pv -w
  set -e
}


function kubectl_watch_pvc() {
  set +e
  print_ntimes "#" 100
  echo "[INFO] GET PVC in watch mode. CTRL+C to continue."
  kubectl get pvc -w --namespace todo
  set -e
}

function kubectl_apply_list() {
  print_ntimes "#" 100

  local LIST=$@

  for yaml in $LIST; do
    if [ -n "$yaml" ]; then
      print_ntimes "=" 100
      echo "[INFO] : kubectl apply -f $yaml"
      print_ntimes "-" 100
      kubectl apply -f config/${yaml}
    fi
  done

}

function kubectl_apply_config() {
  kubectl_apply_list $@
  if [[ "$TASK" == *"V"* ]]; then
    kubectl_describe_namespace
    kubectl_describe_configmap
    kubectl_describe_secret
  fi
}

function kubectl_apply_pv() {
  kubectl_apply_list $@
  if [[ "$TASK" == *"V"* ]]; then
    if [[ "$TASK" == *"WAIT"* ]]; then
      kubectl_watch_pv
    fi
  fi
}
function kubectl_apply_pvc() {
  kubectl_apply_list $@
  if [[ "$TASK" == *"V"* ]]; then
    if [[ "$TASK" == *"WAIT"* ]]; then
      kubectl_watch_pvc
    fi
  fi
}

function kubectl_apply_pods() {
  kubectl_apply_list $@
  if [[ "$MODE" == *"V"* ]]; then
    if [[ "$MODE" == *"WAIT"* ]]; then
      kubectl_watch_pods_svc_deploy
    fi
  fi
}

function kubectl_apply_svc() {
  kubectl_apply_list $@
  if [[ "$MODE" == *"V"* ]]; then
    if [[ "$MODE" == *"WAIT"* ]]; then
      kubectl_watch_svc
    fi
  fi
}

function kubectl_describe_secret() {
  print_ntimes "#" 100
  echo "[INFO] Descripe Secret"
  print_ntimes "-" 100
  kubectl describe secret --namespace todo
  if [[ "$MODE" == *"WAIT"* ]]; then
    read -p "[PAUSE] Press ENTER to continue."
    print_ntimes "-" 100
  fi
}

function kubectl_describe_namespace() {
  print_ntimes "#" 100
  echo "[INFO] Descripe Namespace"
  print_ntimes "-" 100
  kubectl describe namespace todo
  if [[ "$MODE" == *"WAIT"* ]]; then
    read -p "[PAUSE] Press ENTER to continue."
    print_ntimes "-" 100
  fi
}

function kubectl_describe_configmap() {
  print_ntimes "#" 100
  echo "[INFO] Descripe ConfigMap"
  print_ntimes "-" 100
  kubectl describe configmap --namespace todo
  if [[ "$MODE" == *"WAIT"* ]]; then
    read -p "[PAUSE] Press ENTER to continue."
    print_ntimes "-" 100
  fi
}
function kubectl_describe_list_deploy_svc() {

  local DEPLOYMENTS_AND_SERVICES=$@

  print_ntimes "#" 100
  for deployment in $DEPLOYMENTS_AND_SERVICES; do
    print_ntimes "=" 100
    echo "[INFO] Get INFO about DEPLOYMENT of $deployment"
    print_ntimes "-" 100
    kubectl describe deployment $deployment --namespace todo
    if [[ "$MODE" == *"WAIT"* ]]; then
      read -p "[PAUSE] Press ENTER to continue."
      print_ntimes "-" 100
    fi

    print_ntimes "=" 100
    echo "[INFO] Get INFO about SERVICE of $deployment"
    print_ntimes "-" 100
    kubectl describe service $deployment --namespace todo
    if [[ "$MODE" == *"WAIT"* ]]; then
      read -p "[PAUSE] Press ENTER to continue."
      print_ntimes "-" 100
    fi

  done
}

function kubectl_describe_list_deploy() {

  local DEPLOYMENTS=$@

  print_ntimes "#" 100
  for deployment in $DEPLOYMENTS; do
    print_ntimes "=" 100
    echo "[INFO] Get INFO about DEPLOYMENT of $deployment"
    print_ntimes "-" 100
    kubectl describe deployment $deployment --namespace todo
    if [[ "$MODE" == *"WAIT"* ]]; then
      read -p "[PAUSE] Press ENTER to continue."
      print_ntimes "-" 100
    fi

  done
}

function kubectl_describe_list_svc() {
  local SERVICES=$@

  print_ntimes "#" 100
  for service in $SERVICES; do
    print_ntimes "=" 100
    echo "[INFO] Get INFO about SERVICE of $service"
    print_ntimes "-" 100
    kubectl describe service $service --namespace todo
    if [[ "$MODE" == *"WAIT"* ]]; then
      read -p "[PAUSE] Press ENTER to continue."
      print_ntimes "-" 100
    fi

  done

}

function kubectl_get_pvc() {
  print_ntimes "#" 100
  echo "[INFO] Get PVC"
  print_ntimes "-" 100
  kubectl get pvc --namespace todo
  if [[ "$MODE" == *"WAIT"* ]]; then
    read -p "[PAUSE] Press ENTER to continue."
    print_ntimes "-" 100
  fi
}

function kubectl_get_pv() {
  print_ntimes "#" 100
  echo "[INFO] Get PV"
  print_ntimes "-" 100
  kubectl get pv --namespace todo
  if [[ "$MODE" == *"WAIT"* ]]; then
    read -p "[PAUSE] Press ENTER to continue."
    print_ntimes "-" 100
  fi

}

function kubectl_get_svc() {
  print_ntimes "#" 100
  echo "[INFO] Get SVC"
  print_ntimes "-" 100
  kubectl get svc --namespace todo
  if [[ "$MODE" == *"WAIT"* ]]; then
    read -p "[PAUSE] Press ENTER to continue."
    print_ntimes "-" 100
  fi

}

function kubectl_get_pods_info() {
  print_ntimes "#" 100
  echo "[INFO] Get info about PODS"
  print_ntimes "=" 100
  if [[ "$MODE" == *"WAIT"* ]]; then
    kubectl_watch_pods_svc_deploy
  else
    kubectl get pods --namespace todo -o wide
  fi

}

function kubectl_get_pods_list_logs() {
  if [[ "$MODE" == *"VV"* ]]; then
    print_ntimes "#" 100
    echo "[INFO] Get list of PODS "
    PODS=$(kubectl get pods --namespace todo -o name)
    print_ntimes "#" 100
    for pod in $PODS; do
      print_ntimes "=" 100
      echo "[INFO] Get LOGS about PODS $pod"
      print_ntimes "-" 100
      kubectl logs --namespace todo $pod
      if [[ "$MODE" == *"WAIT"* ]]; then
        read -p "[PAUSE] Press ENTER to continue."
        print_ntimes "-" 100
      fi
    done
  fi
}
