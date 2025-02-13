#!/bin/bash

# Exit on any error
set -e

echo "
   _____                       _                  _____ 
  / ____|                     | |           /\   |_   _|
 | (___  _ __   __ _ _ __   __| | __ _     /  \    | |  
  \___ \| '_ \ / _\` | '_ \ / _'| / _' |   / /\ \   | |  
  ____) | |_) | (_| | | | | (_| | (_| |_ / ____ \ _| |_ 
 |_____/| .__/ \__,_|_| |_|\__,_|\__,_(_)_/    \_\_____| 
        | |                                             
        |_|   
"

# Prompt user to choose between CPU or GPU setup
echo "Choose your setup type:"
echo "1. CPU"
echo "2. GPU"
read -rp "Enter the number (1 or 2): " SETUP_TYPE

# Validate input
if [[ "$SETUP_TYPE" != "1" && "$SETUP_TYPE" != "2" ]]; then
  echo "❌ Invalid input! Please choose either 1 (CPU) or 2 (GPU)."
  exit 1
fi

# Set compose file based on user input
if [[ "$SETUP_TYPE" == "1" ]]; then
  COMPOSE_FILE="docker-compose-cpu.yml"
  echo "🔧 Selected setup: CPU"
else
  COMPOSE_FILE="docker-compose-gpu.yml"
  echo "🔧 Selected setup: GPU"
fi

# Store the root directory path
ROOT_DIR=$(pwd)

echo "🌐 Creating platform network if it doesn't exist..."
docker network inspect platform_network >/dev/null 2>&1 || docker network create platform_network

echo "🌐 Creating app_network if it doesn't exist..."
docker network inspect app_network >/dev/null 2>&1 || docker network create app_network

echo "🚀 Starting main services with Docker Compose..."
docker compose -f "$COMPOSE_FILE" up -d

echo "📂 Changing to dockprom directory..."
cd observability/dockprom || {
    echo "❌ Error: dockprom directory not found!"
    echo "Creating dockprom directory..."
    mkdir dockprom
    cd dockprom
}

echo "🚀 Starting monitoring services in dockprom..."
docker compose up -d

# Return to root directory
cd "$ROOT_DIR"

echo "⏳ Waiting for services to be healthy..."
sleep 10

echo "✨ Checking service status..."
echo "Main services:"
docker compose ps
echo -e "\nMonitoring services:"
cd observability/dockprom && docker compose ps

echo "🎉 Deployment complete! All services are now running."
echo "
📝 Access points:
- Grafana: http://localhost:3000 (username - admin/ password - admin)
- Prometheus: http://localhost:9090
- AlertManager: http://localhost:9093
- Kafka: http://localhost:9092
- Redis: http://localhost:6379
- MySQL: http://localhost:3306
- Ollama: http://localhost:11434
- Verba: http://localhost:8000"
