#!/bin/bash
# Exit immediately if any command fails.
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

# Save the repository's root directory.
ROOT_DIR=$(pwd)

# Ensure required Docker networks exist.
echo "🌐 Ensuring required Docker networks exist..."
docker network inspect platform_network >/dev/null 2>&1 || docker network create platform_network
docker network inspect app_network      >/dev/null 2>&1 || docker network create app_network

# ====================================================================
# 1. Process Docker Compose files in the root directory.
# ====================================================================
echo "📂 Processing Docker Compose files in the root directory..."
shopt -s nullglob
for file in docker-compose*.yml; do
  if [[ -f "$file" ]]; then
    # Remove "docker-compose-" prefix and ".yml" suffix.
    base=$(basename "$file")
    friendly_name=${base#docker-compose-}
    friendly_name=${friendly_name%.yml}
    while true; do
      read -rp "Do you want to run '$friendly_name'? (y/n): " yn
      case $yn in
        [Yy]* )
          if [[ "$friendly_name" == "vllm" ]]; then
            read -rp "Enter command for vllm: " vllm_command
            echo "🚀 Running $friendly_name with command '$vllm_command'..."
            COMMAND="$vllm_command" docker compose -f "$file" up -d
          else
            echo "🚀 Running $friendly_name..."
            docker compose -f "$file" up -d
          fi
          break
          ;;
        [Nn]* )
          echo "⏩ Skipping $friendly_name."
          break
          ;;
        * )
          echo "Please answer yes (y) or no (n)."
          ;;
      esac
    done
  fi
done

# ====================================================================
# 2. Process each subdirectory containing Docker Compose files.
# ====================================================================

# Find all directories (at any depth) that contain a file matching 'docker-compose*.yml'
mapfile -t DIRS < <(find . -type f -name "docker-compose*.yml" -printf '%h\n' | sort -u)

for d in "${DIRS[@]}"; do
  # Skip the root directory since it was already processed.
  if [ "$d" == "." ]; then
    continue
  fi

  echo "📂 Entering directory: $d"
  pushd "$d" > /dev/null

  # For each Docker Compose file in the directory, ask the user whether to run it.
  for file in docker-compose*.yml; do
    if [[ -f "$file" ]]; then
      # Remove "docker-compose-" prefix and ".yml" suffix.
      base=$(basename "$file")
      friendly_name=${base#docker-compose-}
      friendly_name=${friendly_name%.yml}
      while true; do
        read -rp "Do you want to run '$friendly_name' in directory '$d'? (y/n): " yn
        case $yn in
          [Yy]* )
            if [[ "$friendly_name" == "vllm" ]]; then
              read -rp "Enter command for vllm: " vllm_command
              echo "🚀 Running $friendly_name in $d with command '$vllm_command'..."
              COMMAND="$vllm_command" docker compose -f "$file" up -d
            else
              echo "🚀 Running $friendly_name in $d..."
              docker compose -f "$file" up -d
            fi
            break
            ;;
          [Nn]* )
            echo "⏩ Skipping $friendly_name."
            break
            ;;
          * )
            echo "Please answer yes (y) or no (n)."
            ;;
        esac
      done
    fi
  done

  popd > /dev/null
done

# Give services some time to start.
echo "⏳ Waiting for services to stabilize..."
sleep 10

echo "🎉 Deployment complete! All services are now running."
echo "
📝 Access points:
- Grafana: http://localhost:3000 (username: admin / password: admin)
- Prometheus: http://localhost:9090
- AlertManager: http://localhost:9093
- Kafka: http://localhost:9092
- Redis: http://localhost:6379
- MySQL: http://localhost:3306
- Ollama: http://localhost:11434
- Verba: http://localhost:8000
"
