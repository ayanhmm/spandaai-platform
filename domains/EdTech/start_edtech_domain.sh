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

    # Start services in background
    (cd data_preprocessing && python3 api.py &) 
    (cd document_analysis && python3 api.py &)
    (cd edu_ai_agents && python3 api.py &)
    (cd qa_generation && python3 api.py &)
    (cd face_analysis && python3 api.py &)

    echo "All services have been started!"
    
    # Start API Gateway in foreground
    cd api_gateway
    docker compose up
else
    echo "Invalid option. Please enter 'docker' or 'local'."
    exit 1
fi
