#!/bin/bash

echo "Starting AFE component Services..."
echo "================================"

echo ""
echo "Choose Model Inference Type:"
echo "1. GPU-based inference (Recommended for better performance)"
echo "2. CPU-based inference (For systems without GPU)"
echo ""
read -p "Enter your choice (1 or 2): " INFERENCE_CHOICE

if [ "$INFERENCE_CHOICE" == "1" ]; then
    INFERENCE_TYPE="GPU"
    COMPOSE_FILE="docker-compose-ollama-gpu.yml"
    OLLAMA_CONTAINER="ollama-platform-gpu"
    EDTECH_COMPOSE_FILE="docker-compose-lecture-video-analysis-gpu.yml"
    echo "Selected: GPU-based inference"
elif [ "$INFERENCE_CHOICE" == "2" ]; then
    INFERENCE_TYPE="CPU"
    COMPOSE_FILE="docker-compose-ollama-cpu.yml"
    OLLAMA_CONTAINER="ollama-platform-cpu"
    EDTECH_COMPOSE_FILE="docker-compose-lecture-video-analysis.yml"
    echo "Selected: CPU-based inference"
else
    echo "Invalid choice. Defaulting to GPU-based inference."
    INFERENCE_TYPE="GPU"
    COMPOSE_FILE="docker-compose-ollama-gpu.yml"
    OLLAMA_CONTAINER="ollama-platform-gpu"
    EDTECH_COMPOSE_FILE="docker-compose-lecture-video-analysis-gpu.yml"
fi

echo ""
echo "Configuration Setup..."
echo "----------------------"
echo "For the services to work properly, we need your Hugging Face token."
echo "You can get one from: https://huggingface.co/settings/tokens"
echo ""
read -p "Enter your Hugging Face token: " HF_TOKEN

if [ -z "$HF_TOKEN" ]; then
    echo "Warning: No Hugging Face token provided. Some services may not work properly."
    echo "You can add it later to the .env files manually."
    HF_TOKEN="put-your-hf-token-here"
fi

echo ""
read -p "Press Enter to continue..."

# Get the current directory (should be profile-scripts)
PROFILE_SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Components Scripts Directory: $PROFILE_SCRIPTS_DIR"

# Navigate to the repository root (one level up from profile-scripts)
cd "$PROFILE_SCRIPTS_DIR/.."
REPO_ROOT="$(pwd)"
echo "Repository Root: $REPO_ROOT"

echo ""
echo "Setting up configuration files..."
echo "---------------------------------"

# Function to create .env from env.example and add HF token
setup_env_file() {
    local TARGET_DIR="$1"
    echo "Setting up .env in: $TARGET_DIR"
    
    if [ ! -d "$TARGET_DIR" ]; then
        echo "Warning: Directory $TARGET_DIR does not exist. Skipping..."
        return
    fi
    
    cd "$TARGET_DIR"
    
    if [ -f "env.example" ]; then
        if [ ! -f ".env" ]; then
            echo "Creating .env from env.example..."
            cp "env.example" ".env"
            echo ".env created from env.example"
        else
            echo ".env already exists, checking for HF token..."
        fi
        
        # Add or update Hugging Face token in .env
        echo "" >> ".env"
        echo "# External Services" >> ".env"
        echo "HUGGINGFACE_TOKEN=$HF_TOKEN" >> ".env"
        echo "Added/Updated Hugging Face token in .env"
    else
        if [ ! -f ".env" ]; then
            echo "No env.example found, creating basic .env with HF token..."
            echo "# External Services" > ".env"
            echo "HUGGINGFACE_TOKEN=$HF_TOKEN" >> ".env"
            echo "Created basic .env with HF token"
        else
            echo ".env exists but no env.example found, adding HF token..."
            echo "" >> ".env"
            echo "# External Services" >> ".env"
            echo "HUGGINGFACE_TOKEN=$HF_TOKEN" >> ".env"
            echo "Added HF token to existing .env"
        fi
    fi
}

# Setup environment files
setup_env_file "$REPO_ROOT/foundation/data_management/Setup/DataStorage"
setup_env_file "$REPO_ROOT/domains/EdTech/lecture-analysis/docker"
setup_env_file "$REPO_ROOT/solutions/EdTech/multimodal_afe_frontend/docker"

echo "Configuration files setup complete!"

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
echo "Starting Spanda.AI EdTech domain - $INFERENCE_TYPE version..."
echo "--------------------------------------------------"
cd "$REPO_ROOT/domains/EdTech/lecture-analysis/docker"
docker compose -f "$EDTECH_COMPOSE_FILE" up -d
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
echo "All AFE component Services Started Successfully!"
echo "========================================"
echo ""
echo "Services started in detached mode:"
echo "1. Docker Networks Created"
echo "2. Configuration files (.env) created/updated with your HF token"
echo "3. Spanda.AI Data Storage"
echo "4. Spanda.AI Inference Engine - on device ($INFERENCE_TYPE)"
echo "   * Other inference options available in /foundation/inference"
echo "   * gemma3:4b model pulled and ready"
echo "5. Spanda.AI EdTech domain - $INFERENCE_TYPE version"
echo "6. Spanda.AI Multi-modal Lecture Content and Delivery Analysis"
echo ""
echo "All services are running in the background."
echo "Use 'docker-compose down' in respective directories to stop services."
echo "Use 'docker ps' to view running containers."
echo ""
echo "AFE component Services deployment complete!"
echo "Go to http://localhost:3001/multimodal to try out the application! Note that wait times will be long depending on Hardware."
echo ""
read -p "Press Enter to exit..."