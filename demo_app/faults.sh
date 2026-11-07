#!/usr/bin/env bash
set -euo pipefail

COMPOSE="docker compose -f demo_app/docker-compose.yml"
DEPLOY_LOG="demo_app/deploys.jsonl"

log_deploy() {
  printf '{"ts":"%s","service":"%s","from":"%s","to":"%s","note":"%s"}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "$2" "$3" "$4" >> "$DEPLOY_LOG"
}

post_fault() {
  curl -fsS -X POST "localhost:$1/admin/faults" -H 'content-type: application/json' \
    -d "{\"name\":\"$2\",\"params\":$3}" > /dev/null
}

case "${1:-}" in
  bad_deploy)
    PAYMENTS_VERSION=v1.1.0 PAYMENTS_BAD_DEPLOY=1 $COMPOSE up -d --force-recreate --no-deps payments
    log_deploy payments v1.0.0 v1.1.0 "release: merchant tier handling"
    ;;
  db_pool_exhaustion)
    curl -fsS -X POST "localhost:8001/admin/hold-connections?seconds=${2:-150}" > /dev/null
    ;;
  memory_leak)
    post_fault 8002 memory_leak '{}'
    ;;
  slow_payments)
    post_fault 8002 slow_payments '{"delay_ms":3000}'
    ;;
  config_error)
    ORDERS_VERSION=v1.0.1 PAYMENTS_URL=http://payments:8003 $COMPOSE up -d --force-recreate --no-deps orders
    log_deploy orders v1.0.0 v1.0.1 "config: update service endpoints"
    ;;
  service_crash)
    $COMPOSE stop payments
    ;;
  reset)
    $COMPOSE up -d --force-recreate --no-deps payments orders
    log_deploy payments reset v1.0.0 "restored baseline"
    log_deploy orders reset v1.0.0 "restored baseline"
    ;;
  *)
    echo "usage: bash demo_app/faults.sh {bad_deploy|db_pool_exhaustion|memory_leak|slow_payments|config_error|service_crash|reset}"
    exit 1
    ;;
esac
echo "done: ${1:-}"
