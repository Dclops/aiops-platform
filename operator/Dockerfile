FROM python:3.11-slim
WORKDIR /operator
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY train_model.py .
COPY incident_engine.py .
COPY k8s_actor.py .
COPY operator_loop.py .
RUN python train_model.py
ENV PYTHONUNBUFFERED=1
CMD ["python", "-u", "operator_loop.py"]
