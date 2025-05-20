# Use Python 3.9 as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt /app/requirements.txt

# Install system dependencies, Python packages, and Go
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    procps \
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

# Create necessary directories
RUN mkdir -p /app/data /app/templates /app/static

# Copy application files
COPY app.py db_handler.py init_db.py ./
COPY templates/ ./templates/
COPY static/ ./static/

# Expose port for Flask app
EXPOSE 8700

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV APPLICATION_ROOT=/contentmaster


# Create Volume for persistent data
VOLUME /app/data

# Initialize the database
RUN python init_db.py

# Start the Flask application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8700", "app:application"]
