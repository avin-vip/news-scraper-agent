FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config.json .
COPY main.py poller.py filter.py notifier.py state.py ./

# state.json is written at runtime; mount a volume to persist across restarts:
# docker run -v $(pwd)/state.json:/app/state.json --env-file .env set-router
CMD ["python", "main.py"]
