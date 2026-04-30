from flask import Flask, request, jsonify
import time
import threading
import random
from prometheus_client import Counter, Gauge, generate_latest, REGISTRY

app = Flask(__name__)

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
CPU_LOAD_GAUGE = Gauge('simulated_cpu_load_percent', 'Simulated CPU load percentage')
MEMORY_GAUGE = Gauge('simulated_memory_usage_mb', 'Simulated memory usage in MB')
ERROR_COUNT = Counter('simulated_errors_total', 'Total simulated errors')

state = {"cpu_load": 0, "memory_mb": 0, "error_rate": 0}
leaked_memory = []

def baseline_metrics():
    while True:
        if state['cpu_load'] == 0:
            CPU_LOAD_GAUGE.set(random.uniform(2, 15))
        if state['memory_mb'] == 0:
            MEMORY_GAUGE.set(random.uniform(100, 250))
        time.sleep(5)

threading.Thread(target=baseline_metrics, daemon=True).start()

def simulate_cpu_work(load_percent, duration_sec):
    end_time = time.time() + duration_sec
    while time.time() < end_time:
        if random.random() * 100 < load_percent:
            _ = sum([x**2 for x in range(1000)])
        else:
            time.sleep(0.05)

def reset_state_after(duration_sec):
    time.sleep(duration_sec)
    state['cpu_load'] = 0
    state['memory_mb'] = 0

@app.route('/health')
def health():
    REQUEST_COUNT.labels(method='GET', endpoint='/health').inc()
    return jsonify({"status": "healthy"})

@app.route('/api/status')
def api_status():
    return jsonify(state)

@app.route('/metrics')
def metrics():
    REQUEST_COUNT.labels(method='GET', endpoint='/metrics').inc()
    return generate_latest(REGISTRY), 200, {'Content-Type': 'text/plain'}

@app.route('/simulate', methods=['POST'])
def simulate():
    REQUEST_COUNT.labels(method='POST', endpoint='/simulate').inc()
    data = request.get_json() or {}
    cpu_load = data.get('cpu_load', 0)
    memory_mb = data.get('memory_mb', 0)
    duration = data.get('duration', 30)
    error_rate = data.get('error_rate', 0)
    state['cpu_load'] = cpu_load
    state['memory_mb'] = memory_mb
    state['error_rate'] = error_rate
    CPU_LOAD_GAUGE.set(cpu_load)
    MEMORY_GAUGE.set(memory_mb)
    if cpu_load > 0:
        threading.Thread(target=simulate_cpu_work, args=(cpu_load, duration), daemon=True).start()
        threading.Thread(target=reset_state_after, args=(duration,), daemon=True).start()
    if memory_mb > 0:
        try:
            leaked_memory.append(bytearray(memory_mb * 1024 * 1024))
        except MemoryError:
            return jsonify({"error": "Memory allocation failed"}), 500
    if error_rate > 0 and random.random() * 100 < error_rate:
        ERROR_COUNT.inc()
        return jsonify({"error": "Simulated error"}), 500
    return jsonify({"message": "Injecting CPU:{}% Mem:{}MB for {}s".format(cpu_load, memory_mb, duration), "state": state})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
