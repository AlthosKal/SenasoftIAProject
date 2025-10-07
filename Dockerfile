# ================================
# STAGE 1: Build Dependencies
# ================================
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create directory for dependencies
WORKDIR /deps

# Copy requirements and install dependencies in separate directory
COPY requirements-docker.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --target=/deps -r requirements.txt

# ================================
# STAGE 2: Production Runtime
# ================================
FROM python:3.11-slim AS production

# Only install curl for health checks (no build tools)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy compiled dependencies from builder stage
COPY --from=builder /deps /usr/local/lib/python3.11/site-packages/

# Copy only necessary application files
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Environment variables for optimization
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 5000

# Optimized health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Run application
CMD ["python", "app.py"]