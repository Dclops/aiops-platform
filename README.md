# AIOps Platform: Autonomous Kubernetes Remediation

A closed-loop AIOps system: Observe -> Detect -> Decide -> Act -> Stabilize -> Recover

## Architecture
Flask App -> Prometheus (5s) -> Operator (10s) -> ML + Rules -> K8s API -> Scale 1<->4

## Production Evidence
Scale Up: [ALERT] Critical CPU threshold breach (90.0%) -> Scaled 1->4
Scale Down: [Info] Low CPU -> Scaled 4->1

## Tech: Kubernetes, Prometheus, scikit-learn, Flask, Docker, Python
