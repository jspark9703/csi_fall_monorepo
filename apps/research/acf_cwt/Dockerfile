# ── Stage 1: builder ──────────────────────────────────────────────────────────
# ARG BASE_IMAGE allows CPU/GPU switching:
# CPU:  docker build -f apps/research/Dockerfile .
# GPU:  docker build -f apps/research/Dockerfile --build-arg BASE_IMAGE=nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04 .

ARG BASE_IMAGE=python:3.11-slim
FROM ${BASE_IMAGE} AS builder

COPY --from=ghcr.io/astral-sh/uv:0.6.11 /uv /usr/local/bin/uv

WORKDIR /build

COPY pyproject.toml uv.lock ./
COPY shared/ ./shared/
COPY apps/research/ ./apps/research/

RUN uv sync --frozen \
        --package fall-sensing-research \
        --no-dev \
        --no-editable

# ── Stage 2: runtime ─────────────────────────────────────────────────────────
ARG BASE_IMAGE=python:3.11-slim
FROM ${BASE_IMAGE} AS runtime

RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-create-home appuser

WORKDIR /app

COPY --from=builder /build/.venv /app/.venv

RUN mkdir -p /data/processed /data/models && \
    chown -R appuser:appgroup /data

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    DATA_ROOT=/data/processed \
    MODEL_OUTPUT=/data/models

USER appuser

CMD ["python", "-m", "fall_sensing.research.train"]
