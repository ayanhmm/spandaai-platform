#!/bin/bash

# Spanda AI Platform - Data Management Services Startup Script
# This script starts all data management services in the correct order

echo "[*] Starting Spanda AI Platform Data Management Services..."
echo "=================================================="

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting services in dependency order..."
echo

# Function to check if a service started successfully
check_service_start() {
    if [ $? -eq 0 ]; then
        echo "    [OK] $1 containers started"
    else
        echo "    [X] Failed to start $1"
    fi
}



# 1. Start Data Storage (Database/Storage layer first)
echo "[1] Starting Data Storage..."
cd "$SCRIPT_DIR/DataStorage"
if [ -f "Data-Storage.yml" ]; then
    echo "    Running: docker-compose -f Data-Storage.yml up -d"
    docker-compose -f Data-Storage.yml up -d
    check_service_start "Data Storage"
else
    echo "    [!] Data-Storage.yml not found, skipping..."
fi
echo

# 2. Start Data Lake (Storage layer)
echo "[2] Starting Data Lake..."
cd "$SCRIPT_DIR/DataLake"
if [ -f "Data-Lake.yml" ]; then
    echo "    Running: docker-compose -f Data-Lake.yml up -d"
    docker-compose -f Data-Lake.yml up -d
    check_service_start "Data Lake"
else
    echo "    [!] Data-Lake.yml not found, skipping..."
fi
echo

# 3. Start Data Ingestion (Input layer)
echo "[3] Starting Data Ingestion..."
cd "$SCRIPT_DIR/DataIngestion"
if [ -f "Data-Ingestion.yml" ]; then
    echo "    Running: docker-compose -f Data-Ingestion.yml up -d"
    docker-compose -f Data-Ingestion.yml up -d
    check_service_start "Data Ingestion"
else
    echo "    [!] Data-Ingestion.yml not found, skipping..."
fi
echo

# 4. Start Data Processing (Processing layer)
echo "[4] Starting Data Processing..."
cd "$SCRIPT_DIR/DataProcessing"
if [ -f "Data-Processing.yml" ]; then
    echo "    Running: docker-compose -f Data-Processing.yml up -d"
    docker-compose -f Data-Processing.yml up -d
    check_service_start "Data Processing"
else
    echo "    [!] Data-Processing.yml not found, skipping..."
fi
echo

# 5. Start Data Analytics (Analysis layer)
echo "[5] Starting Data Analytics..."
cd "$SCRIPT_DIR/DataAnalytics"
if [ -f "Data-Analytics.yml" ]; then
    echo "    Running: docker-compose -f Data-Analytics.yml up -d"
    docker-compose -f Data-Analytics.yml up -d
    check_service_start "Data Analytics"
else
    echo "    [!] Data-Analytics.yml not found, skipping..."
fi
echo

# Return to original directory
cd "$SCRIPT_DIR"

echo "=================================================="
echo "[*] All services startup completed!"
echo

# Wait a moment for services to initialize
echo "[~] Waiting 10 seconds for services to initialize..."
sleep 10

echo "Checking service status..."
echo "----------------------"

# Check common service ports
check_port_status 5432
check_port_status 9000
check_port_status 9092
check_port_status 8080
check_port_status 3000

echo
echo "[i] To view all running containers:"
echo "   docker ps"
echo
echo "[i] To view service logs, use:"
echo "   docker-compose -f DataStorage/Data-Storage.yml logs -f"
echo "   docker-compose -f DataLake/Data-Lake.yml logs -f"
echo "   docker-compose -f DataIngestion/Data-Ingestion.yml logs -f"
echo "   docker-compose -f DataProcessing/Data-Processing.yml logs -f"
echo "   docker-compose -f DataAnalytics/Data-Analytics.yml logs -f"
echo
echo "[i] To stop all services, use:"
echo "   docker-compose -f DataStorage/Data-Storage.yml down"
echo "   docker-compose -f DataLake/Data-Lake.yml down"
echo "   docker-compose -f DataIngestion/Data-Ingestion.yml down"
echo "   docker-compose -f DataProcessing/Data-Processing.yml down"
echo "   docker-compose -f DataAnalytics/Data-Analytics.yml down"
echo
echo "[*] Spanda AI Platform - Data Management Layer startup complete!"

echo
echo "Press any key to continue..."
read -n 1 -s