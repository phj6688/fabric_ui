# Use Python 3.9 as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt .

# Install system dependencies and Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

# Download and install Fabric for ARM64
RUN curl -L https://github.com/danielmiessler/fabric/releases/latest/download/fabric-linux-arm64 > /usr/local/bin/fabric && \
    chmod +x /usr/local/bin/fabric

# Create data directory
RUN mkdir -p /app/data

# Copy application files
COPY ui.py .
COPY fabric_api.py .
COPY db_handler.py .
COPY init_db.py .

# Install streamlit-option-menu
RUN pip install --no-cache-dir streamlit-option-menu

# Expose only port 8700 for external access
EXPOSE 8700

# Copy startup script
COPY start.sh .
RUN chmod +x start.sh

# Set environment variables
ENV STREAMLIT_SERVER_PORT=8700
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV PATH="/usr/local/bin:${PATH}"

# Create Volume
VOLUME /app/data

# Initialize the database
RUN python init_db.py

# Run both services using the startup script
CMD ["./start.sh"]