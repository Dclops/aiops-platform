from prometheus_api_client import PrometheusConnect
from incident_engine import IncidentDecisionEngine
from k8s_actor import KubernetesActor
import time
import os
import warnings

warnings.filterwarnings("ignore")

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus-server.default.svc.cluster.local")
DEPLOYMENT_NAME = os.getenv("TARGET_DEPLOYMENT", "demo-app")
NAMESPACE = os.getenv("TARGET_NAMESPACE", "default")
INTERVAL = int(os.getenv("CHECK_INTERVAL", "10"))
COOLDOWN = int(os.getenv("COOLDOWN_SECONDS", "60"))

last_action_time = 0


def fetch_metrics(prom):
    try:
        cpu_q = "max_over_time(simulated_cpu_load_percent[1m])"
        mem_q = "max_over_time(simulated_memory_usage_mb[1m])"
        r1 = prom.custom_query(cpu_q)
        r2 = prom.custom_query(mem_q)
        cpu = float(r1[0]["value"][1]) if r1 else 0.0
        mem = float(r2[0]["value"][1]) if r2 else 0.0
        return {"cpu": cpu, "memory": mem, "latency": 0.2}
    except Exception as e:
        print("[Warn] " + str(e))
        return None


def can_act():
    global last_action_time
    now = time.time()
    if now - last_action_time > COOLDOWN:
        last_action_time = now
        return True
    return False


prom = PrometheusConnect(url=PROMETHEUS_URL, disable_ssl=True)
engine = IncidentDecisionEngine()
actor = KubernetesActor(namespace=NAMESPACE)

print("=" * 50)
print("  AIOps Platform v15 - Production Operator")
print("  Target: " + DEPLOYMENT_NAME)
print("  Cooldown: " + str(COOLDOWN) + "s")
print("=" * 50)

while True:
    try:
        m = fetch_metrics(prom)
        if not m:
            time.sleep(INTERVAL)
            continue

        print("[Monitor] CPU: {:.1f}% | Mem: {:.1f}MB".format(m["cpu"], m["memory"]))

        d = engine.assess(m)

        if d and d["action"] == "SCALE_UP":
            print("[ALERT] " + d["reason"])
            if can_act():
                cur = actor.get_replicas(DEPLOYMENT_NAME)
                if cur < 4:
                    print("[Action] Scaling " + DEPLOYMENT_NAME + " " + str(cur) + " -> 4")
                    actor.scale_deployment(DEPLOYMENT_NAME, 4)
                else:
                    print("[Skip] Already at max replicas")
            else:
                print("[Skip] Cooldown active")
        elif d and d["action"] == "SCALE_DOWN":
            print("[Info] " + d["reason"])
            if can_act():
                cur = actor.get_replicas(DEPLOYMENT_NAME)
                if cur > 1:
                    print("[Action] Scaling " + DEPLOYMENT_NAME + " " + str(cur) + " -> 1")
                    actor.scale_deployment(DEPLOYMENT_NAME, 1)
                else:
                    print("[Skip] Already at min replicas")
            else:
                print("[Skip] Cooldown active")
        elif d:
            print("[Info] " + d["reason"])
        else:
            print("[Status] Nominal")

    except Exception as e:
        print("[Error] " + str(e))

    time.sleep(INTERVAL)
