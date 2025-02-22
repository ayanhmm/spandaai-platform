FROM python:3.10-slim

# Install system dependencies including the Docker CLI
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

    
# Install Node.js and npm, then install promptfoo globally
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g promptfoo

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 7100

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7100"]
