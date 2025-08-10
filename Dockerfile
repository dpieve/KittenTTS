# Multi-stage build for smaller runtime images
# 1) Base image with Python and system deps
FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    HF_HOME=/cache/huggingface \
    XDG_CACHE_HOME=/cache

# System packages needed for soundfile/libsndfile and espeak
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsndfile1 \
    espeak-ng \
    && rm -rf /var/lib/apt/lists/*

# 2) Builder image to install python deps (kept separate for caching)
FROM base AS builder
WORKDIR /app

# Copy metadata to leverage Docker layer caching
COPY requirements.txt pyproject.toml setup.py README.md ./

# Pre-build dependency wheels to maximize cache reuse across code changes
RUN pip install --upgrade pip \
    && pip wheel --wheel-dir /wheels -r requirements.txt

# Copy source only after deps are cached to avoid invalidating dep layer
COPY kittentts ./kittentts

# Build project wheel
RUN pip wheel --no-deps --wheel-dir /wheels .

# 3) Final runtime image
FROM base AS runtime
WORKDIR /app

# Create a non-root user for better security
RUN useradd -ms /bin/bash appuser

# Copy wheels from builder and install
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links /wheels kittentts \
    && rm -rf /wheels

# Add a simple CLI for TTS testing
COPY scripts/tts_cli.py /usr/local/bin/tts
RUN chmod +x /usr/local/bin/tts

# Default working directory for outputs mounted by users
RUN mkdir -p /data /cache && chown -R appuser:appuser /data /cache
USER appuser

# Default command shows help
ENTRYPOINT ["/usr/local/bin/tts"]
CMD ["--help"]
