#!/usr/bin/env bash

echo "[INFO] begin POSTGRESS readiness probe..."
if [[ -n "${POSTGRES_USER}" ]]; then
  pg_isready -h localhost -U "${POSTGRES_USER}"
else
  echo "[ERROR] POSTGRES_USER not defined"
  exit 1
fi
echo "[INFO] end POSTGRESS readiness probe."
