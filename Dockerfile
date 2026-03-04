FROM python:3.11-slim

LABEL maintainer="fanji-jared"
LABEL description="BSM-QQ-Server - QQ Bot for Minecraft Bedrock Server Management"

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai

RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

RUN mkdir -p /app/logs

VOLUME ["/app/logs"]

CMD ["python", "-m", "src.main"]
