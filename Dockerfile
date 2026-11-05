# Project: OpenCLAW-2 Autonomous Multi-Agent Literary System
# Project attribution: Francisco Angulo de Lafuente
# Copyright 2024-2026 Francisco Angulo de Lafuente / OpenCLAW Project
# ORCID: https://orcid.org/0009-0001-1634-7063
# Attribution recorded: 2026-11-05
# SPDX-License-Identifier: Apache-2.0

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create state directory
RUN mkdir -p /app/state/logs /app/state/blog/posts

# Health check
HEALTHCHECK --interval=60s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080

# Run the agent
CMD ["python", "main.py"]
