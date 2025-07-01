#!/bin/bash

DIR="${1:-.}"
declare -A PORTS

open_browser() {
    URL=$1
    if command -v xdg-open > /dev/null; then
        xdg-open "$URL"
    elif command -v open > /dev/null; then
        open "$URL"
    else
        echo "Please open your browser and visit: $URL"
    fi
}

echo "Searching for docker-compose YAMLs in '$DIR'..."

for file in "$DIR"/*.yml "$DIR"/*.yaml; do
    [ -e "$file" ] || continue
    echo -e "\n📄 Found YAML file: $file"
    
    # List services defined in the YAML
    services=($(docker-compose -f "$file" config --services))
    
    if [ ${#services[@]} -eq 0 ]; then
        echo "⚠️ No services found in $file"
        continue
    fi

    echo "Available services:"
    for i in "${!services[@]}"; do
        echo "$((i+1)). ${services[$i]}"
    done

    read -p "Enter comma-separated service numbers to launch (or press Enter to skip): " input
    [[ -z "$input" ]] && continue

    IFS=',' read -ra selected <<< "$input"
    selected_services=()
    for i in "${selected[@]}"; do
        index=$((i-1))
        if [[ $index -ge 0 && $index -lt ${#services[@]} ]]; then
            selected_services+=("${services[$index]}")
        fi
    done

    if [ ${#selected_services[@]} -eq 0 ]; then
        echo "⚠️ No valid services selected. Skipping..."
        continue
    fi

    echo " Launching: ${selected_services[*]} from $file"
    docker-compose -f "$file" up -d "${selected_services[@]}"

    # Extract host ports
    while IFS= read -r line; do
        port=$(echo "$line" | awk -F ':' '{print $1}' | tr -d ' -')
        if [[ $port =~ ^[0-9]+$ ]]; then
            PORTS[$port]=1
        fi
    done < <(grep -E '^\s*-\s*[0-9]+:[0-9]+' "$file")
done

sleep 5

echo -e "\n🌐 Opening exposed ports in browser..."

for port in "${!PORTS[@]}"; do
    echo "🔗 http://localhost:$port"
    open_browser "http://localhost:$port"
done
