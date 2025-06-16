# Setup Instructions

### 1. Create Docker Compose File

- Create a new directory for the project, then create a copy of the file named `Data-Processing.yml` 

### 2. Set Up a network 
- Create a new network for communication with other modules of the pipeline and list all networks to check if network properly created
   ```bash
   docker network create Spanda-Net
   docker network ls
   ```

## Set Up Dremio for Data Processing

- Start the Dremio service:
   ```bash
   docker-compose -f Data-Processing.yml up -d dremio
   ```

- Check if the containr is connected to the required network
   ```bash
   docker network inspect Spanda-Net
   ```

- Access the Dremio UI at http://localhost:9047 and set up an admin account

- Configure Dremio to Connect to Nessie/MinIO - Make sure both are running
   - Click "Add a Source" and select "Nessie"
   - **General settings tab:**
     - Source Name: `nessie`
     - Nessie Endpoint URL: `http://nessie:19120/api/v2`
     - Auth Type: `None`
   - **Storage settings tab:**
     - AWS Root Path: `warehouse`
     - AWS Access Key: `admin`
     - AWS Secret Key: `password`
     - Uncheck "Encrypt Connection" Box
   - **Connection Properties:**
     - Key: `fs.s3a.path.style.access` | Value: `true`
     - Key: `fs.s3a.endpoint` | Value: `minio:9000`
     - Key: `dremio.s3.compat` | Value: `true`
   - Click "Save"

### Dremio Connection Issues
#### If Dremio can't connect to Nessie or MinIO:
1. Make sure all services are running: `docker-compose ps`
2. Check if the network is properly configured
3. Try using container IP addresses instead of hostnames in connection settings
