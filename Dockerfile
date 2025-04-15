FROM python:3.12.4-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir alembic

COPY . .

RUN echo '#!/bin/sh\n\
alembic upgrade head\n\
uvicorn main:app --host 0.0.0.0 --port 8000 --reload' > /app/start.sh && \
chmod +x /app/start.sh

CMD ["/app/start.sh"]