FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app/ownerpay

# System deps for pandas/pyarrow
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY ownerpay/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY ownerpay /app/ownerpay

ENV PYTHONPATH=/app/ownerpay \
    PORT=8000

EXPOSE 8000

CMD ["uvicorn", "src.ownerpay.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]


