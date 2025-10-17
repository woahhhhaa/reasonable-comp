FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for pandas/pyarrow
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps from repo root requirements (matches local dev)
COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source code and data used by the kernel
COPY src ./src
COPY data ./data

ENV PYTHONPATH=/app:/app/src \
    PORT=8000

EXPOSE 8000

CMD ["uvicorn", "src.ownerpay.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]


