#!/bin/bash

echo "Do you want to run the services using Docker or locally? (Enter 'docker' or 'local')"
read mode

if [ "$mode" == "docker" ]; then
    echo "Starting EdTech services with Docker..."
    
    # Run docker-compose in the background
    docker compose up -d 

    echo "All services have been started in the background!"
    
    # Navigate to api_gateway and start Docker Compose in foreground
    cd api_gateway
    docker compose up

elif [ "$mode" == "local" ]; then
    echo "Starting EdTech services locally..."

    # Start services in separate terminals
    gnome-terminal -- bash -c "cd data_preprocessing && python api.py; exec bash"
    gnome-terminal -- bash -c "cd document_analysis && python api.py; exec bash"
    gnome-terminal -- bash -c "cd edu_ai_agents && python api.py; exec bash"
    gnome-terminal -- bash -c "cd qa_generation && python api.py; exec bash"
    gnome-terminal -- bash -c "cd face_analysis && python api.py; exec bash"

    echo "All services have been started!"
    
    # Start API Gateway in foreground
    cd api_gateway
    docker compose up
else
    echo "Invalid option. Please enter 'docker' or 'local'."
    exit 1
fi
