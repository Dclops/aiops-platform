# AIOps Platform: Autonomous Kubernetes Remediation

**Closed-loop AIOps system**: Observe -> Detect -> Decide -> Act -> Stabilize -> Recover

## Architecture
```
Flask App -> Prometheus (5s) -> Operator (10s) -> ML + Rules -> K8s API -> Scale (1<->4)
```

## Hybrid Decision Engine
- Isolation Forest (ML) - Detects unknown patterns
- CPU Threshold (85%) - Deterministic safety guarantee
- Low CPU (<30%) - Auto scale-down
- 60s Cooldown - Anti-thrashing protection

## Production Evidence
**Scale Up:** [ALERT] CPU 90.0% -> Scaled 1->4
**Scale Down:** [Info] Low CPU -> Scaled 4->1

## Tech Stack
Kubernetes | Prometheus | scikit-learn | Flask | Docker | Python
