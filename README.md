> Built a production-style closed-loop AIOps system with autonomous scaling on Kubernetes using ML anomaly detection + rule-based safeguards.

---

# AIOps Platform: Autonomous Kubernetes Remediation

**Closed-loop AIOps system**: Observe -> Detect -> Decide -> Act -> Stabilize -> Recover

---

## System Flow

User Load -> Flask App (Metrics) -> Prometheus (5s) -> Operator (10s) -> ML + Rules Engine -> Kubernetes API -> Scale (1<->4)

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
- ML alone = unsafe in production (probabilistic)
- Rules alone = rigid, misses unknown patterns
- Hybrid = intelligence + safety guarantees

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| max_over_time[1m] | Avoid reacting to noisy spikes; capture sustained load |
| 60s cooldown | Prevent thrashing (rapid scale up/down oscillations) |
| Replica bounds (1-4) | Cost control + cluster stability |
| Bi-directional scaling | Full lifecycle: handle load, then recover to baseline |
| ML + Rules hybrid | ML finds unknowns; thresholds ensure safety |

---

## Production Evidence (v15)

Scale Up (Load Detected):
[Monitor] CPU: 90.0% | Mem: 249.5MB
[ALERT] Critical CPU threshold breach (90.0%)
[Action] Scaling demo-app 1 -> 4

Scale Down (Cost Optimization):
[Info] Low CPU - scaling down (13.7%)
Replicas: 1

Stabilization:
[Skip] Cooldown active

---

## Quick Start

minikube start --cpus=4 --memory=4096
kubectl apply -f app/deployment.yaml
helm install prometheus prometheus-community/prometheus
kubectl apply -f operator/deployment.yaml

Test:
kubectl port-forward svc/demo-app 5000:5000 &
curl -X POST http://localhost:5000/simulate -H "Content-Type: application/json" -d '{"cpu_load":90,"duration":60}'
kubectl logs -f deployment/aiops-operator
---

## Tech Stack

Kubernetes | Prometheus | scikit-learn | Flask | Docker | Python
## Interview Pitch

"I built a closed-loop AIOps system on Kubernetes where Prometheus captures time-windowed metrics, a hybrid ML + rules engine detects anomalies, and a custom operator performs autonomous remediation including both scale-up and scale-down with cooldown protection to prevent thrashing."

---

Demonstrates: Kubernetes operators, Prometheus observability, ML in production, system design, reliability engineering, and cost-aware automation.
---


