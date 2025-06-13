# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

WORKDIR /arbeitszeitapp

# Builder stage: install dependencies in a venv
FROM base AS builder

# Install build dependencies (if any are needed, e.g. gcc, libpq-dev, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    apt-get purge -y --auto-remove && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements files first for better cache usage
COPY --link requirements-dev.txt requirements-dev.txt
COPY --link requirements.txt requirements.txt
COPY --link constraints.txt constraints.txt

# Create venv and install dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m venv .venv && \
    .venv/bin/pip install --upgrade pip && \
    .venv/bin/pip install --requirement requirements-dev.txt

# Copy the rest of the application code
COPY --link . .

# Final stage: minimal image with app and venv
FROM base AS final

WORKDIR /arbeitszeitapp

# Create non-root user
RUN addgroup --system arbeitszeit && adduser --system --ingroup arbeitszeit arbeitszeit

# Copy from builder
COPY --from=builder /arbeitszeitapp /arbeitszeitapp

ENV PATH="/arbeitszeitapp/.venv/bin:$PATH"
ENV ARBEITSZEITAPP_CONFIGURATION_PATH="/arbeitszeitapp/arbeitszeit_flask/development_settings.py"
ENV FLASK_APP=arbeitszeit_flask
ENV FLASK_DEBUG=0
ENV DEV_DATABASE_URI="postgresql://postgres@host.docker.internal:5432/Arbeitszeitapp_dev"
ENV DEV_SECRET_KEY="my_secret_key"
ENV ARBEITSZEIT_APP_SERVER_NAME="host.docker.internal:5000"
ENV ARBEITSZEITAPP_TEST_DB="postgresql://postgres@host.docker.internal:5432/Arbeitszeitapp_test"
# Ensure Python outputs logs in real-time
ENV PYTHONUNBUFFERED=1
# Install gunicorn if not already in requirements
RUN if ! python -c "import gunicorn" &> /dev/null; then \
        .venv/bin/pip install gunicorn; \
    fi
# Set permissions for the application directory
RUN chown -R arbeitszeit:arbeitszeit /arbeitszeitapp && \
    chmod -R 755 /arbeitszeitapp

# Expose the default Flask port
ENV PORT=5000
EXPOSE ${PORT}

# Use non-root user
USER arbeitszeit

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:5000 \"${FLASK_APP}.wsgi:app\""]
