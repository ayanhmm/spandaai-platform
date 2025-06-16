# Setup Instructions

### 1. Create Docker Compose File

- Create a new directory for the project, then create a copy of the file named `Data-Analytics.yml` 

### 2. Set Up a network 
- Create a new network for communication with other modules of the pipeline and list all networks to check if network properly created
   ```bash
   docker network create Spanda-Net
   docker network ls
   ```

## Set Up Superset for BI Dashboards

- Start the Superset service:
   ```bash
   docker-compose -f Data-Analytics.yml up -d superset
   ```

- Initialize Superset:
   ```bash
   docker exec -it superset superset init
   ```

-  Check if the containr is connected to the required network
   ```bash
   docker network inspect Spanda-Net
   ```   

- Access Superset at http://localhost:8088 and log in:
   - Username: `admin`
   - Password: `admin`

- Add a Dremio connection:
   - Go to "Settings" > "Database Connections"
   - Click "Add a database" > Select "Other"
   - Create a display name for your dataset.
   - Enter connection string:
     ```
     dremio+flight://USERNAME:PASSWORD@dremio:32010/?UseEncryption=false
     ```
     (Replace USERNAME and PASSWORD with your Dremio credentials)
   - You must URL-encode any special character in the username or password that could interfere with the URL structure 

      | Character | Meaning in URL                                  | Encoded As |
      | --------- | ----------------------------------------------- | ---------- |
      | `@`       | Separates user/pass from host                   | `%40`      |
      | `:`       | Separates user from password, or host from port | `%3A`      |
      | `/`       | Indicates path segments                         | `%2F`      |
      | `?`       | Starts query parameters                         | `%3F`      |
      | `#`       | Starts a fragment                               | `%23`      |
      | `&`       | Separates query parameters                      | `%26`      |
      | `=`       | Separates key and value in query                | `%3D`      |
      | `+`       | Space (in some cases)                           | `%2B`      |
      | `%`       | Escape character itself                         | `%25`      |

      ✅ **Safe Characters (No Encoding Needed)**  
      Alphanumeric (`A-Z`, `a-z`, `0-9`) and a few others:

      - `-` (hyphen)  
      - `_` (underscore)  
      - `.` (dot)  
      - `~` (tilde)

   - Test connection and save

- Create a dataset:
   - Click the "+" icon > "Create dataset"
   - Select the database connection you want to analyze
   - Choose the desired table
   - Save

- Build dashboards:
   - Create charts based on your dataset
   - Add charts to dashboards for visualization

## Set Up Rath for Data Exploration
- Clone the Rath repository and open it
   ```bash
   git clone https://github.com/Kanaries/Rath.git
   cd Rath
   ```

- Launcg the application via YARN
   ```bash
   yarn install
   yarn workspace rath-client build
   yarn workspace rath-client start
   ```
