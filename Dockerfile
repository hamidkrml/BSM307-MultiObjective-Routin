# BSM307 Multi-Objective Routing - Dockerfile
# Python 3.10 slim base image
FROM python:3.10-slim

# Metadata
LABEL maintainer="BSM307 Project"
LABEL description="Multi-Objective Routing with GA, ACO, RL, SA algorithms"
LABEL version="1.0"

# Working directory
WORKDIR /app

# System dependencies for matplotlib and GUI support
RUN apt-get update && apt-get install -y \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libfontconfig1 \
    libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Python cache temizle (build sırasında)
RUN find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find . -name "*.pyc" -delete 2>/dev/null || true && \
    find . -name "*.pyo" -delete 2>/dev/null || true

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy and set permissions for entrypoint script (as root)
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Switch to non-root user
USER appuser

# Set entrypoint (script executable by all)
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Default command (can be overridden)
CMD ["python", "demo.py"]

