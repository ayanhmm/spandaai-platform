#!/bin/bash

echo "Starting AFE Bundle Services..."
echo "================================"

echo ""
echo "Choose LLM Inference Type:"
echo "1. GPU-based inference (Recommended for better performance)"
echo "2. CPU-based inference (For systems without GPU)"
echo ""
read -p "Enter your choice (1 or 2): " INFERENCE_CHOICE

if [ "$INFERENCE_CHOICE" = "1" ]; then
    INFERENCE_TYPE="GPU"
    COMPOSE_FILE="docker-compose-ollama-gpu.yml"
    OLLAMA_CONTAINER="ollama-platform-gpu"
    echo "Selected: GPU-based inference"
elif [ "$INFERENCE_CHOICE" = "2" ]; then
    INFERENCE_TYPE="CPU"
    COMPOSE_FILE="docker-compose-ollama-cpu.yml"
    OLLAMA_CONTAINER="ollama-platform-cpu"
    echo "Selected: CPU-based inference"
else
    echo "Invalid choice. Defaulting to GPU-based inference."
    INFERENCE_TYPE="GPU"
    COMPOSE_FILE="docker-compose-ollama-gpu.yml"
    OLLAMA_CONTAINER="ollama-platform-gpu"
fi

echo ""
read -p "Press Enter to continue..."

# Get the current directory (should be profile-scripts)
PROFILE_SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Profile Scripts Directory: $PROFILE_SCRIPTS_DIR"

# Navigate to the repository root (one level up from profile-scripts)
REPO_ROOT="$(dirname "$PROFILE_SCRIPTS_DIR")"
echo "Repository Root: $REPO_ROOT"

echo ""
echo "Creating Docker Networks..."
echo "---------------------------"
docker network create dev-network 2>/dev/null || echo "Network dev-network already exists or created"
docker network create Spanda-Net --driver bridge 2>/dev/null || echo "Network Spanda-Net already exists or created"
docker network create platform_network 2>/dev/null || echo "Network platform_network already exists or created"
docker network create app_network 2>/dev/null || echo "Network app_network already exists or created"
echo "Docker networks created/verified successfully"

echo ""
echo "Starting Spanda.AI Data Storage..."
echo "----------------------------------"
cd "$REPO_ROOT/foundation/data_management/Setup/DataStorage"
docker compose -f Data-Storage.yml up -d
if [ $? -eq 0 ]; then
    echo "Spanda.AI Data Storage started successfully"
else
    echo "Error starting Spanda.AI Data Storage"
    read -p "Press Enter to exit..."
    exit 1
fi

echo ""
echo "Starting Spanda.AI Inference Engine - on device ($INFERENCE_TYPE)..."
echo "--------------------------------------------------"
echo "Note: Other inference options exist for production - check /foundation/inference directory"
cd "$REPO_ROOT/foundation/inference/cpu-optimized-gguf"
docker compose -f "$COMPOSE_FILE" up -d
if [ $? -eq 0 ]; then
    echo "Spanda.AI Inference Engine started successfully"
    
    echo ""
    echo "Waiting for Ollama container to be ready..."
    sleep 10
    
    echo "Pulling gemma3:4b model..."
    echo "---------------------------"
    docker exec -it "$OLLAMA_CONTAINER" ollama pull gemma3:4b
    if [ $? -eq 0 ]; then
        echo "gemma3:4b model pulled successfully"
    else
        echo "Warning: Failed to pull gemma3:4b model. You may need to pull it manually later."
        echo "Command: docker exec -it $OLLAMA_CONTAINER ollama pull gemma3:4b"
    fi
else
    echo "Error starting Spanda.AI Inference Engine"
    read -p "Press Enter to exit..."
    exit 1
fi

echo ""
echo "Starting Spanda.AI EdTech domain - slim version..."
echo "--------------------------------------------------"
cd "$REPO_ROOT/domains/EdTech/lecture-analysis/docker"
docker compose -f docker-compose-lecture-video-analysis.yml up -d
if [ $? -eq 0 ]; then
    echo "Spanda.AI EdTech domain backend started successfully"
else
    echo "Error starting Spanda.AI EdTech domain backend"
    read -p "Press Enter to exit..."
    exit 1
fi

echo ""
echo "Starting Spanda.AI Multi-modal Lecture Content and Delivery Analysis..."
echo "-----------------------------------------------------------------------"
cd "$REPO_ROOT/solutions/EdTech/multimodal_afe_frontend/docker"
docker compose -f docker-compose-images.yml up -d
if [ $? -eq 0 ]; then
    echo "Spanda.AI Multi-modal Frontend started successfully"
else
    echo "Error starting Spanda.AI Multi-modal Frontend"
    read -p "Press Enter to exit..."
    exit 1
fi

echo ""
echo "========================================"
echo "All AFE Bundle Services Started Successfully!"
echo "========================================"
echo ""
echo "Services started in detached mode:"
echo "1. Docker Networks Created"
echo "2. Spanda.AI Data Storage"
echo "3. Spanda.AI Inference Engine - on device ($INFERENCE_TYPE)"
echo "   * Other inference options available in /foundation/inference"
echo "   * gemma3:4b model pulled and ready"
echo "4. Spanda.AI EdTech domain - slim version"
echo "5. Spanda.AI Multi-modal Lecture Content and Delivery Analysis"
echo ""
echo "All services are running in the background."
echo "Use 'docker-compose down' in respective directories to stop services."
echo "Use 'docker ps' to view running containers."
echo ""
echo "AFE Bundle Services deployment complete!"
echo "Go to http://localhost:3001/multimodal to try out the application! Note that wait times will be long depending on Hardware."
echo ""
read -p "Press Enter to exit..."