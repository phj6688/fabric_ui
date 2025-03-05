# Use Python 3.9 as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

COPY requirements.txt /app/requirements.txt

# Install system dependencies, Python packages, and Go
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    procps \
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

# Install Go (ARM64 version for Linux)
RUN curl -L https://go.dev/dl/go1.21.5.linux-arm64.tar.gz | tar -C /usr/local -xz

# Set up Go environment variables
ENV GOROOT=/usr/local/go
ENV GOPATH=/go
ENV PATH="$GOROOT/bin:$GOPATH/bin:$PATH"

# Verify Go installation
RUN go version

# Install Fabric using Go
RUN go install github.com/danielmiessler/fabric@latest

# Ensure Fabric is accessible globally
RUN ln -s /go/bin/fabric /usr/local/bin/fabric

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
ENV APP_TITLE="ContentMaster AI"

# Create Volume
VOLUME /app/data

# Initialize the database
RUN python init_db.py

# Run both services using the startup script
CMD ["./start.sh"]
