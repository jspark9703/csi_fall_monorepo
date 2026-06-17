# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.6.11 /uv /usr/local/bin/uv

WORKDIR /build

# Copy workspace-level config so uv can resolve the lockfile
COPY pyproject.toml uv.lock ./

# Copy shared core (needed as workspace dependency)
COPY shared/ ./shared/

# Copy only this app's source
COPY apps/infrastructure/ ./apps/infrastructure/

# Install the app + its workspace dependencies into /build/.venv
RUN uv sync --frozen \
        --package fall-sensing-infrastructure \
        --no-dev \
        --no-editable

# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-create-home appuser

WORKDIR /app

# Copy only the virtualenv produced by the builder — no build tools needed
COPY --from=builder /build/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

USER appuser

CMD ["python", "-m", "fall_sensing.infra.mqtt_listener"]
