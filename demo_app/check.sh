#!/usr/bin/env bash
echo "== Firing alerts (Prometheus) =="
curl -s localhost:9090/api/v1/alerts \
  | jq -r '.data.alerts[] | select(.state=="firing") | "\(.labels.alertname)  \(.labels.service // .labels.job)"' | sort -u
echo
echo "== Last alerts delivered to the receiver =="
docker compose -f demo_app/docker-compose.yml logs --no-log-prefix --tail 200 alert-sink \
  | grep "alert received" | tail -5
echo
echo "== Recent warning and error logs (Loki) =="
curl -sG localhost:3100/loki/api/v1/query_range \
  --data-urlencode 'query={service=~"orders|payments|api-gateway"} |~ `"level": "(ERROR|WARNING)"`' \
  --data-urlencode 'limit=6' | jq -r '.data.result[].values[][1]' | head -6
