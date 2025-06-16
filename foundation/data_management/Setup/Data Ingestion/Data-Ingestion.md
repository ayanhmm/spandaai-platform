# Setup Instructions

#### 1. Create Docker Compose File

- Create a new directory for the project, then create a copy of the file named `Data-Ingestion.yml` 

#### 2. Set Up a network 
- Create a new network for communication with other modules of the pipeline and list all networks to check if network properly created
  ```bash
   docker network create Spanda-Net
   docker network ls
   ```

## Set Up Spark for Data Ingestion

- Start the Spark service:
   ```bash
   docker-compose -f Data-Ingestion.yml up -d spark
   ```

- Check if the containr is connected to the required network
   ```bash
   docker network inspect Spanda-Net
   ```

- Access the Spark Jupyter Notebook interface at http://localhost:8888



## Set up Kafka for Real Time Pipelines
- Start the Kafka + Zookeeper service:
   ```bash
   docker-compose -f Data-Ingestion.yml up -d kafka zookeeper
   ```

- Check if the container is connected to the required network
   ```bash
   docker network inspect Spanda-Net
   ```

- Move inside the kafka container
   ```bash
   docker exec -it kafka bash 
   ```

- Create a Topic for data flow
   ```bash
   kafka-topics --create \
  --topic sensor_topic \
  --bootstrap-server kafka:9092 \
  --partitions 1 --replication-factor 1
   ```

- List all topics
   ```bash
   kafka-topics --list --bootstrap-server kafka:9092
   ```

- Delete a topic
   ```bash
   kafka-topics --bootstrap-server kafka:9092 --delete --topic sensor_topic
   ```

- Come out of the container
   ```bash
   exit
   ```



## Set up Nifi for Data Handling
- Start the nifi service:
   ```bash
   docker-compose -f Data-Ingestion.yml up -d nifi
   ```

- Check if the container is connected to the required network.

-  Access the Nifi UI at https://localhost:8443/nifi
   
- Log in using credentials 
   - username = `admin` 
   - password = `password1234`


##  Utilize Spark for Video Data Ingestion
- Copy the videos folder to Spark container
   ```bash
   docker cp Sample_Videos spark:/workspace/videos
   ```
   Make sure folder named Sample_Videos is present in the same folder as docker-compose else change path accordingly.

- Locate IP Address of Minio Server
   ```bash
   docker inspect minio | grep IPAddress
   ```
   This ip address is the value that will be assigned to the variable minio_ip when spark is communicating to minio

- Run the Jupyter Notebook named `Videos Ingestion.ipynb`
First, it saves videos to a minio bucket and then creates a nessie catalog and metadata for those videos

##  Utilize Spark for Database Setup and Ingestion
- Set up the Database source 
   - Make sure the database source is up and running.
   - Refer to the readme file associated with Data Storage to set up Postgres.
   - Check its on the same network
      ```bash
      docker network inspect Spanda-Net
      ```
   - Create database if not already exists
      ```bash
      docker exec -it postgres psql -U myuser mydb
      ```
- Copy the folder containing the database to the Postgres and Spark container
   - Make sure folder named Sample_Tables is present in the same folder as docker-compose else change path accordingly.
      ```bash
      docker cp Sample_Tables postgres:/tables
      docker cp Sample_Tables spark:/workspace/tables
      ```
   
   - Checking if properly uploaded
      ```bash
      docker exec -it postgres /bin/sh
      ls
      ```
      Folder names `tables` should be visible

- Locate IP Address of Minio Server
   ```bash
   docker inspect minio | grep IPAddress
   ```
   This ip address is the value that will be assigned to the variable minio_ip when spark is communicating to minio

-  Run the Jupyter Notebook named `Database Ingestion.ipynb`
      - First, it creates a database for all the tables saved in .csv format inside a cammon folder and then uploads them to a minio bucket and creates a nessie catalog and metadata for the database
      - Note: It only assigns data types to table columns, you may also want to assign integrity counstraints yourself
      - If You want to skip the data Creation Part and ingest data from already running databases, simply skip the heading `Uploading all tables from a Folder to a Database`.



##  Real time Data Ingestion via Kafka and Spark
- Make sure the source is Publishing
   
- Locate IP Address of Minio Server
   ```bash
   docker inspect minio | grep IPAddress
   ```
   This ip address is the value that will be assigned to the variable minio_ip when spark is communicating to minio

- Locate IP Address of Kafka Server
   ```bash
   docker inspect kafka | grep IPAddress
   ```
   This ip address is the value that will be assigned to the variable kafka_ip when spark is communicating to minio

- Run the Jupyter Notebook named `Ingestion_real_time.ipynb`
It saves real time data from kafka to a minio bucket and creates a nessie for the same.



## Setting up `Sample_Producer.py` as a real time source
   - Save the script to same folder as docker compose
   - Copy the script to the kafka container
      ```bash
      docker cp Sample_Producer.py kafka:/produce.py
      ``` 
   - Access the container to run the script
      ```bash
      docker exec -it kafka bash 
      ``` 
   - Make sure that you are in the root folder inside the container
      ```bash
      cd ../../
      ls
      ``` 
   - Install the python kafka package inside the container
      ```bash
      pip3 install kafka-python
      ``` 
   - Run the script
      ```bash
      python3 produce.py 
      ``` 
   - Now the producer is online and has started producing


## Additional Resources

- [Dremio Documentation](https://docs.dremio.com/)
- [Apache Iceberg Documentation](https://iceberg.apache.org/docs/latest/)
- [Nessie Documentation](https://projectnessie.org/documentation/)
- [Apache Superset Documentation](https://superset.apache.org/docs/intro)

## Next Steps

After completing this tutorial, you might want to:
1. Add more data sources to Dremio
2. Create more complex transformations with Spark
3. Build comprehensive dashboards in Superset
4. Implement data governance policies

---

*Based on the ["End-to-End Basic Data Engineering Tutorial"](https://medium.com/data-engineering-with-dremio/end-to-end-basic-data-engineering-tutorial-spark-dremio-superset-c076a56eaa75) by Alex Merced *