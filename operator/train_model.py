from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import pandas as pd
import numpy as np
print("Training model with production-grade baseline...")
np.random.seed(42)
n = 500
normal_cpu = np.concatenate([
    np.random.uniform(0, 5, 100),
    np.random.uniform(5, 15, 100),
    np.random.uniform(15, 40, 300),
])
normal_mem = np.random.normal(200, 50, n)
normal_lat = np.random.normal(0.1, 0.05, n)
anom_cpu = np.random.uniform(75, 100, 50)
anom_mem = np.random.normal(500, 100, 50)
anom_lat = np.random.normal(1.5, 0.3, 50)
cpu = np.concatenate([normal_cpu, anom_cpu])
memory = np.concatenate([normal_mem, anom_mem])
latency = np.concatenate([normal_lat, anom_lat])
df = pd.DataFrame({"cpu": cpu, "memory": memory, "latency": latency})
features = df[["cpu", "memory", "latency"]]
scaler = StandardScaler()
scaled = scaler.fit_transform(features)
model = IsolationForest(contamination=0.08, random_state=42)
model.fit(scaled)
joblib.dump(model, "model.joblib")
joblib.dump(scaler, "scaler.joblib")
print("Model trained: Normal=0-40%, Anomaly=75-100%")
