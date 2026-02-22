FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends bash procps git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY index.html server.py refresh.sh themes.json config.json ./

RUN chmod +x refresh.sh

EXPOSE 8080

ENTRYPOINT ["python3", "server.py", "--bind", "0.0.0.0"]
