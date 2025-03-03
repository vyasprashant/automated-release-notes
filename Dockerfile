FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && \
    apt-get install -y curl ca-certificates libopenblas-dev && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /app/output /app/.streamlit
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY .streamlit/config.toml /app/.streamlit/config.toml
ENV DOCKER_ENV=true
CMD ["python", "entry.py"]
#CMD ["streamlit", "run", "ui.py", "--server.port=8501", "--server.address=0.0.0.0"]