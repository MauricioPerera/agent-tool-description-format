# Multi-stage build for optimized production image
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first for better caching
COPY requirements.txt requirements-vector.txt ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r requirements-vector.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    ATDF_ENV=production

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r atdf && useradd -r -g atdf atdf

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=atdf:atdf . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data && \
    chown -R atdf:atdf /app

# Switch to non-root user
USER atdf

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "examples.fastapi_mcp_integration:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

# Development stage (optional)
FROM production as development

# Switch back to root to install dev dependencies
USER root

# Install development dependencies
RUN pip install -r requirements-dev.txt

# Switch back to atdf user
USER atdf

# Override command for development
CMD ["uvicorn", "examples.fastapi_mcp_integration:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]