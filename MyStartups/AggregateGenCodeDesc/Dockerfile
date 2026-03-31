FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends git subversion && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY aggregateGenCodeDesc.py .

ENTRYPOINT ["python3", "aggregateGenCodeDesc.py"]
