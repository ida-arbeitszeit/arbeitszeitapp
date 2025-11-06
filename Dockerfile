# syntax=docker/dockerfile:1

FROM python:3.12-slim AS base

WORKDIR /arbeitszeitapp

# Builder stage: install dependencies in a venv
FROM base AS builder

# Install build dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements files first for better cache usage
COPY --link requirements.txt requirements.txt
COPY --link constraints.txt constraints.txt

# Create venv and install dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m venv .venv && \
    .venv/bin/pip install --upgrade pip && \
    .venv/bin/pip install --requirement requirements.txt --constraint constraints.txt && \
    .venv/bin/pip install --no-cache-dir psycopg2-binary gunicorn

# Copy only application code
COPY --link arbeitszeit/ arbeitszeit/
COPY --link arbeitszeit_db/ arbeitszeit_db/
COPY --link arbeitszeit_development/ arbeitszeit_development/
COPY --link arbeitszeit_flask/ arbeitszeit_flask/
COPY --link arbeitszeit_web/ arbeitszeit_web/

# Final stage: minimal image with app and venv
FROM base AS final

WORKDIR /arbeitszeitapp

# Create non-root user
RUN addgroup --system arbeitszeit && adduser --system --ingroup arbeitszeit arbeitszeit

# Install curl for healthcheck and runtime PostgreSQL libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /arbeitszeitapp/.venv /arbeitszeitapp/.venv

# Copy only application code from builder
COPY --from=builder /arbeitszeitapp/arbeitszeit /arbeitszeitapp/arbeitszeit
COPY --from=builder /arbeitszeitapp/arbeitszeit_db /arbeitszeitapp/arbeitszeit_db
COPY --from=builder /arbeitszeitapp/arbeitszeit_development /arbeitszeitapp/arbeitszeit_development
COPY --from=builder /arbeitszeitapp/arbeitszeit_flask /arbeitszeitapp/arbeitszeit_flask
COPY --from=builder /arbeitszeitapp/arbeitszeit_web /arbeitszeitapp/arbeitszeit_web

ENV PATH="/arbeitszeitapp/.venv/bin:$PATH"
ENV FLASK_APP=arbeitszeit_flask
ENV FLASK_DEBUG=0
ENV PYTHONUNBUFFERED=1
ENV PORT=5000
ENV MPLCONFIGDIR=/tmp/matplotlib

RUN chown -R arbeitszeit:arbeitszeit /arbeitszeitapp && \
    chmod -R 755 /arbeitszeitapp

EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

USER arbeitszeit

# Use --preload to load the app before forking workers (run db migrations only once)
CMD ["gunicorn", "--preload", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "arbeitszeit_flask.wsgi:app"]
