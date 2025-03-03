FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && \
    apt-get install -y curl ca-certificates libopenblas-dev && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /app/output
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV DOCKER_ENV=true
CMD ["python", "cli.py"]
#CMD ["streamlit", "run", "ui.py", "--server.port=8501", "--server.address=0.0.0.0"]