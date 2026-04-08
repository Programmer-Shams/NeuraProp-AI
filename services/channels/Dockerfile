FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy workspace config
COPY pyproject.toml uv.lock ./
COPY libs/core/pyproject.toml libs/core/
COPY libs/core/src/ libs/core/src/
COPY libs/testing/pyproject.toml libs/testing/
COPY libs/testing/src/ libs/testing/src/
COPY services/channels/pyproject.toml services/channels/
COPY services/channels/src/ services/channels/src/

RUN uv sync --frozen --no-dev

# Runtime
FROM python:3.12-slim

WORKDIR /app

COPY --from=base /app /app
COPY --from=base /usr/local/bin/uv /usr/local/bin/uv

ENV APP_ENV=production \
    LOG_LEVEL=INFO

CMD ["uv", "run", "python", "-m", "channels.discord.runner"]
