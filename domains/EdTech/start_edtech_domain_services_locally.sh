#!/bin/bash

echo "Starting EdTech services..."

# Start Data Preprocessing Service
gnome-terminal -- bash -c "cd data_preprocessing && python3 api.py; exec bash"

# Start Document Analysis Service
gnome-terminal -- bash -c "cd document_analysis && python3 api.py; exec bash"

# Start Edu AI Agents Service
gnome-terminal -- bash -c "cd edu_ai_agents && python3 api.py; exec bash"

# Start QA Generation Service
gnome-terminal -- bash -c "cd qa_generation && python3 api.py; exec bash"

echo "All services have been started!"

# Navigate to api_gateway and start Docker Compose
cd api_gateway
docker-compose up
