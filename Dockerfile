# Use Python 3.12 slim image for smaller size
FROM python:3.12-slim

# Set metadata
LABEL maintainer="Sandeep Nalam <nsandeep12@gmail.com>"
LABEL description="Atlassian MCP Server for AI Assistant Integration with Jira & Bitbucket"
LABEL version="1.0.0"
LABEL org.opencontainers.image.title="Atlassian MCP Server"
LABEL org.opencontainers.image.description="Model Context Protocol server for Atlassian products integration"
LABEL org.opencontainers.image.vendor="Sandeep Nalam"
LABEL org.opencontainers.image.licenses="MIT"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MCP_SERVER_HOST=0.0.0.0
ENV MCP_SERVER_PORT=8000

# Create non-root user for security
RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create necessary directories
RUN mkdir -p /app/logs /app/data && \
    chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Create .ssh directory for git operations
RUN mkdir -p /home/mcpuser/.ssh && \
    chmod 700 /home/mcpuser/.ssh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Default command
CMD ["python", "src/main.py"]
