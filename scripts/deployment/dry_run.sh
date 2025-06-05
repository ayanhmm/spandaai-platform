#!/bin/bash
echo "🔍 Validating Docker Compose setup..."
docker compose --env-file .env -f master-compose.yml config

