# Fault scenarios (ground truth for evaluation)

Run with `bash demo_app/faults.sh <name>`; restore with `bash demo_app/faults.sh reset`.

| Fault | What is injected | Root cause | Correct remediation |
|---|---|---|---|
| bad_deploy | payments redeployed as v1.1.0 | Regression in v1.1.0: about 60% of charges raise KeyError | Roll back payments to v1.0.0 |
| db_pool_exhaustion | orders holds all 5 database connections for 150 s | Connection pool exhausted by long-held connections | Restart orders |
| memory_leak | payments caches a 4 MB receipt per charge, never freed | Unbounded receipt cache grows until memory alert | Restart payments, then bound the cache |
| slow_payments | payments adds 3 s delay per charge | Payments latency propagates to orders and gateway | Restart or scale payments, investigate dependency |
| config_error | orders redeployed as v1.0.1 with the wrong payments port | Bad endpoint config in v1.0.1 | Roll back orders to v1.0.0 |
| service_crash | payments container stopped | payments is down | Restart payments |

Alerts: HighErrorRate, HighLatencyP95, HighMemory, ServiceDown (see demo_app/observability/alerts.yml).
