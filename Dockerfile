FROM python:3.9-slim
#FROM pytorch/pytorch:1.12.0-cuda11.3-cudnn8-runtime

WORKDIR /app

RUN apt-get update && \
    apt-get install -y curl  ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/output

COPY requirements.txt .

# Install packages in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DOCKER_ENV=true

CMD ["python", "release_notes_ai.py"]