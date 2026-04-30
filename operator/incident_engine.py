import joblib
import numpy as np

class IncidentDecisionEngine:
    def __init__(self, model_path="model.joblib", scaler_path="scaler.joblib"):
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.cpu_threshold = 70.0
        self.memory_threshold = 400.0
        self.critical_cpu = 85.0
        self.low_cpu = 30.0

    def assess(self, current_metrics):
        features = np.array([[
            current_metrics["cpu"],
            current_metrics["memory"],
            current_metrics["latency"]
        ]])
        scaled = self.scaler.transform(features)
        ai_score = self.model.predict(scaled)[0]
        is_anomaly = (ai_score == -1)
        cpu = current_metrics["cpu"]
        memory = current_metrics["memory"]
        cpu_high = cpu > self.cpu_threshold
        cpu_critical = cpu > self.critical_cpu
        cpu_low = cpu < self.low_cpu
        memory_high = memory > self.memory_threshold

        # HYBRID LOGIC: ML anomaly + deterministic rules
        if is_anomaly and cpu_high:
            return {"action": "SCALE_UP", "reason": "ML anomaly + High CPU ({:.1f}%)".format(cpu)}
        elif cpu_critical:
            return {"action": "SCALE_UP", "reason": "Critical CPU threshold breach ({:.1f}%)".format(cpu)}
        elif is_anomaly and memory_high:
            return {"action": "RESTART", "reason": "ML anomaly + High memory ({:.1f}MB)".format(memory)}
        elif cpu_low:
            return {"action": "SCALE_DOWN", "reason": "Low CPU - scaling down ({:.1f}%)".format(cpu)}
        elif is_anomaly:
            return {"action": "LOG", "reason": "ML anomaly detected, no threshold breached"}
        return None
