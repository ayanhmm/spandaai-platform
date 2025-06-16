# Setup Instructions

### 1. Create Docker Compose File

Create a new directory for the project, then create a copy of the file named `Data-Lake.yml` 

### 2. Set Up a network 
Create a new network for communication with other modules of the pipeline and list all networks to check if network properly created
```bash
   docker network create Spanda-Net
   docker network ls
   ```

## Set Up Nessie as a catalog

- Start the Nessie service:
   ```bash
   docker-compose -f Data-Lake.yml up -d nessie
   ```

- Check if the containr is connected to the required network
   ```bash
   docker network inspect Spanda-Net
   ```

- Access the Nessie UI at http://localhost:19120/

## Set Up Minio for Data Storage
- Start the Minio service:
   ```bash
   docker-compose -f Data-Lake.yml up -d minio
   ```

- Check if the containr is connected to the required network
   ```bash
   docker network inspect Spanda-Net
   ```

- Open MinIO console in your browser: http://localhost:9001
- Login with:
   - Username: `admin`
   - Password: `password`

-  Set Up MinIO Bucket - Create a new bucket named `warehouse`