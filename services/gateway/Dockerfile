FROM python:3.12-slim AS base

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy workspace config
COPY pyproject.toml uv.lock ./
COPY libs/core/pyproject.toml libs/core/
COPY libs/core/src/ libs/core/src/
COPY libs/testing/pyproject.toml libs/testing/
COPY libs/testing/src/ libs/testing/src/
COPY services/gateway/pyproject.toml services/gateway/
COPY services/gateway/src/ services/gateway/src/
COPY services/channels/pyproject.toml services/channels/
COPY services/channels/src/ services/channels/src/

# Install dependencies
RUN uv sync --frozen --no-dev

# Runtime
FROM python:3.12-slim

WORKDIR /app

COPY --from=base /app /app
COPY --from=base /usr/local/bin/uv /usr/local/bin/uv

ENV APP_ENV=production \
    LOG_LEVEL=INFO \
    PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uv", "run", "uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
