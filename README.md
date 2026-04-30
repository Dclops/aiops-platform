# AIOps Platform: Autonomous Kubernetes Remediation

**Closed-loop AIOps system**: Observe -> Detect -> Decide -> Act -> Stabilize -> Recover

---

## Architecture

User Load -> Flask App -> Prometheus (5s) -> Operator (10s) -> ML + Rules -> K8s API -> Scale (1<->4)

---

## Decision Logic

| Condition | Action |
|-----------|--------|
| CPU > 85% | SCALE_UP |
| ML anomaly + CPU high | SCALE_UP |
| CPU < 30% | SCALE_DOWN |
| ML anomaly + memory high | RESTART |
| ML anomaly only | LOG |

### Why Hybrid?
- ML alone = unsafe in production
- Rules alone = rigid
- Hybrid = intelligence + safety

---

## Why max_over_time[1m]?

- Avoids reacting to transient spikes
- Captures sustained load pressure
- Matches production SRE patterns

---

## Production Evidence

Scale Up:
[ALERT] Critical CPU threshold breach (90.0%)
[Action] Scaling demo-app 1 -> 4

Scale Down:
[Info] Low CPU - scaling down (13.7%)
Replicas: 1

---

## Quick Start

minikube start
kubectl apply -f app/deployment.yaml
kubectl apply -f operator/deployment.yaml

---

## Tech Stack

Kubernetes | Prometheus | scikit-learn | Flask | Docker | Python
