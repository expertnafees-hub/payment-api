# ==============================================================================
# STAGE 1: Builder (Compile dependencies)
# ==============================================================================
FROM python:3.11-slim AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .

# Install dependencies into virtualenv, then remove build tools from venv
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt && \
    /opt/venv/bin/pip uninstall -y pip setuptools wheel

# ==============================================================================
# STAGE 2: Final Runtime (Minimal, Zero Build Tools, Non-Root)
# ==============================================================================
FROM python:3.11-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8080

# Attack Surface Reduction: Remove unnecessary base image build packages
RUN rm -rf /usr/local/lib/python3.11/site-packages/pip* \
           /usr/local/lib/python3.11/site-packages/setuptools* \
           /usr/local/lib/python3.11/site-packages/wheel* \
           /usr/local/lib/python3.11/site-packages/easy_install*

# Security: Create non-root user
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /sbin/nologin -M appuser

COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appgroup app.py .

USER appuser:appgroup

EXPOSE 8080

CMD ["gunicorn", "--workers=2", "--threads=2", "--bind=0.0.0.0:8080", "--access-logfile=-", "--error-logfile=-", "app:app"]
