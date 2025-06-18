# AFE Bundle Quick Start

This bundle launches the complete Spanda.AI EdTech platform with multimodal lecture analysis capabilities.

## Prerequisites

- Docker and Docker Compose installed
- For GPU inference: NVIDIA Docker runtime configured
- Sufficient disk space for AI models (~4GB+ for gemma3:4b)

## Quick Start

### Windows
```cmd
# Navigate to profile-scripts directory
cd profile-scripts

# Run the bundle script
afe-bundle.bat
```

### Linux/macOS/WSL
```bash
# Navigate to profile-scripts directory
cd profile-scripts

# Fix line endings (if running on WSL/Linux with Windows-created file)
dos2unix afe-bundle.sh
# OR: sed -i 's/\r$//' afe-bundle.sh

# Make executable and run
chmod +x afe-bundle.sh
./afe-bundle.sh
```

## What Gets Started

The script will launch services in this order:
1. **Docker Networks** - Creates required network infrastructure
2. **Data Storage** - PostgreSQL, Redis, and other data services
3. **Inference Engine** - Ollama with GPU/CPU support
4. **EdTech Domain** - Backend lecture analysis services
5. **Frontend** - Multi-modal analysis interface

## Manual Model Management

If automatic model pulling fails, manually run:
```bash
# For GPU setup
docker exec -it ollama-platform-gpu ollama pull gemma3:4b

# For CPU setup  
docker exec -it ollama-platform-cpu ollama pull gemma3:4b
```

## Important Notes

⚠️ **Model Download**: The script automatically pulls the `gemma3:4b` model (~4GB) when starting Ollama. This may take several minutes depending on your internet connection.

⚠️ **First Run**: Initial startup can take 10-15 minutes as Docker images are pulled and models are downloaded.

## Access the Application

Once started, access the application at:
- **Main Interface**: http://localhost:3001/multimodal
- **Note**: Response times will vary based on your hardware configuration. Generally, for laptops which have weak GPUs/CPU only, it could take a long time to evaluate lectures.

## Managing Services

```bash
# View running containers
docker ps

# Stop all services (run in respective directories)
docker-compose down

# Check service logs
docker-compose logs [service-name]
```

## Troubleshooting

- **Long wait times**: Normal on first run - models are being downloaded
- **GPU not detected**: Choose CPU inference option when prompted
- **Port conflicts**: Ensure ports 3001, 5432, 6379, and others are available
- **Out of disk space**: Ensure 10GB+ free space for all components
