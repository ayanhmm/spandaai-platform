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
  --topic sensor_data \
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

- Read all messages published on a given topic
   ```bash
   kafka-console-consumer \
   --bootstrap-server kafka:9092 \
   --topic temp_data \
   --from-beginning
   ```

- Send dummy data to a topic
   - Console producer command
      ```bash
      kafka-console-producer \
      --broker-list \
      localhost:9092 \
      --topic temp_data
      ```
   - Enter the dummydata
      ```bash
      {"source": "sensor1", "temp": 28.5, "timestamp": "2025-06-13T18:00:00Z"}
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



## Setting up a Python Script as a real time source
   - Mount the scripts to the kafka container:
      - If the scripts were locates in the same folder as docker-compose, they should already be mounted. check via
         ```bash
         docker exec -it kafka bash 
         cd /user_data
         ls
         ``` 
      - Otherwise, Save the `Sample_Producer.py` or `Sample_Producer_2.py` script to same folder as docker compose. Copy the script to the kafka container manually using `docker cp Sample_Producer.py kafka:/user_data/produce.py`

   - Access the container to run the script
      ```bash
      docker exec -it kafka bash 
      cd /user_data
      ``` 
   - Install the python kafka package inside the container
      ```bash
      pip3 install kafka-python
      ``` 
   - Run the script
      ```bash
      python3 produce.py 
      ``` 
   - Now the producer is online and has started producing.
   - You may run both the scripts together to simulate multiple sensors publishing data on same kafka topic.

## Setting up Nifi to publish data to Kafka from a .csv file
- Mount the .csv files to the kafka container:
   - If the scripts were located in the same folder as docker-compose, they should already be mounted. check via
      ```bash
      docker exec -it nifi bash 
      cd /user_data
      ls
      ``` 
   - Otherwise, Save the files to the same folder as docker compose. Copy them to the kafka container manually using `docker cp Sample_Table.csv kafka:/user_data/table.csv`

- Fetching the .csv file from nifi's local directory
   - Set up a new Nifi processor by dragging the processor icon from the top to the canvas. Select `GetFile` as the type of processor.
   - Double click on the newly created processor to open its configuration. Go to the properties tab.
    - Assign the required Properties: (If any of the properties are not visible, press the + icon of Required Fields to add a propery).
      - Input Directory specifies the address of the .csv file inside the nifi container.
      - Specify File Filter: `.*\.csv` so that it only reads the desired files.
      - Keep Source File: false.
- Splitting the .csv file into individual records
   - Set up a new Nifi processor by dragging the processor icon from the top to the canvas. Select `SplitRecore` as the type of processor.
   - Double click on the newly created processor to open its configuration. Go to the properties tab.
    - Assign the required Properties: (If any of the properties are not visible, press the + icon of Required Fields to add a propery).
      - Record Reader specifies the type of file we are reading.for .csv files select `CSVReader`. Inside the configuration settings of the CSVReader, set First Line Is Header to true.
      - Record Writer specifies the format you want to split the file into. Since, we will be publishing the records to kafka, set it to `JsonRecordSetWriter`.
      - Set Records per Split to 1.

- Publish the records to a kafka topic
   - Refer to `Setting up kafka-producer using nifi`

- Forming a relationship among the above processors.
    `GetFile -> splitRecord -> Publish Kafka -> Output port` 

- Set the state of all the processors to running to start publishing.

## Kafka Data Filtering and Transfer using Nifi
- **Setting up a kafka-consumer inside nifi:**
   - Set up a new Nifi processor by dragging the processor icon from the top to the canvas. Select `ConsumeKafka` as the type of processor.
   - Double click on the newly created processor to open its configuration. Go to the properties tab.
   - Assign the required Properties: (If any of the properties are not visible, press the + icon of Required Fields to add a propery).
      - Kafka Connection Service specifies the kafka service port it needs to consume data from.
      - Topics specify the topics it needs to subscribe to.
      - Group ID is the kafka consumer group identifier.  
   - Setting up a Kafka Connection Service:
      - Click on the 3 vertical dots at the end of Kafka Connection Service property and select create new service option
      - select `org.apache.nifi - nifi-kafka-3-service-nar` service type, press add.
      - The new service has been created.
      - Inorder to configure the new service, press the 3 dots again and then select go to service option. It takes you to the Controller Services List window.
      - Select the required service, click at the 3 vertical dots on the right and select edit option
      - Declare The Bootstrap Servers `kafka:9092`. Press the verification tick to check if the connection to the port is created.
      - Apply the changes and change the state of the service to `Enabled` via the 3 vertical dots
   - Return to the processor's configuration settings and press the verificatio tick to check if the required topic can be accessed. Press Apply.
   - Set up a new output port by dragging the icon from the top to the canvas. Give a suitable name to the port.
   - Drag the arrow icon on top of the consume kafka processor to the output port or any suitable output. Specify the prioritizer in the settings tab and press add  to create a relationship `success`.
   - Recieving and inspecting the data recieved:
      - Now a functional kafka consumer has been created which is in the default `Stopped` state, You may change the state to running by clicking the triangular play icon and start recieving data.
      - Right click on the consume kafka box and select `View Data Provenance` to see the list of the data read by the processor.
      - Once inside the provenance tab, select the data item you want to inspect, click on the vertical dots and press View Details.
      - Inside the content tab click view button to read the decoded recieved data.

- **Setting up kafka-producer using nifi:**
   - Set up a new Nifi processor by dragging the processor icon from the top to the canvas. Select `PublishKafka` as the type of processor.
   - Double click on the newly created processor to open its configuration. Go to the properties tab.
   - Assign the required Properties: (If any of the properties are not visible, press the + icon of Required Fields to add a propery).
      - Kafka Connection Service specifies the kafka service port it needs to publish data to.
      - Topic name specify the topics it needs to publish to.
      - Either set Transactions Enabled to false Delivery Guarentee to best effort or to true and Guarentee Delivery depending upon your usecase
      - Set Record rerader to JsonTreeReader. Go to its settings and set Schema Access Strategy: Infer Schema. Click Apply and then enable the service.
      - Set Record Writer to JsonRecordSetWriter. Go to its settings and set Schema Write Strategy: Do Not Write Schema. Click Apply and then enable the service.
   - Form a relationship to the kafka consumer and another to an output service or port.
   - **Note:** Order of data might change. NiFi is a dataflow engine, not a queue. It processes records asynchronously and independently. Even though records arrive in order, NiFi might buffer, route, or process them in parallel, causing reordering.

- **Setting up QueryRecord to filter Kafka data**
   - Set up a new Nifi processor by dragging the processor icon from the top to the canvas. Select `QueryRecord` as the type of processor.
   - Double click on the newly created processor to open its configuration. Go to the properties tab.
   - Assign the required Properties: (If any of the properties are not visible, press the + icon of Required Fields to add a propery).
      - Set Record rerader to JsonTreeReader. Go to its settings and set Schema Access Strategy: Infer Schema. Click Apply and then enable the service.
      - Set Record Writer to JsonRecordSetWriter. Go to its settings and set Schema Write Strategy: Do Not Write Schema. Click Apply and then enable the service.
      - in the Query property, Provide a SQL Query which will be used to filter the data. For instance, `SELECT * FROM FLOWFILE WHERE source = 'sensor1'` filters all the data coming from sensor 1.
         **Note:** If the query field does not exist by default, press the + icon of Required Fields to add a propery.
   - Form a relationship to the kafka consumer and another to the kafka publisher.
   - Now, the publisher will only publish the data points which satisfy the given query.
   - This is usefull in segregating data from different sensors or filtering data according to specific needs.

- **Setting up ConvertRecord to convert Kafka data format**
   - Set up a new Nifi processor by dragging the processor icon from the top to the canvas. Select `ConvertRecord` as the type of processor.
   - Double click on the newly created processor to open its configuration. Go to the properties tab.
   - Assign the required Properties: (If any of the properties are not visible, press the + icon of Required Fields to add a propery).
      - Set Record rerader to JsonTreeReader or whatever the format of the incoming data is. Go to its settings and set Schema Access Strategy: Infer Schema. Click Apply and then enable the service.
      - Set Record Writer to the format you want to convert the data to. Go to its settings and set Schema Write Strategy: Do Not Write Schema. Click Apply and then enable the service.
   - Form a relationship to the kafka consumer and another to the kafka publisher.
   - Now, the publisher will only publish the data points in the newly declared format.

- **Other useful Processors:**
   - **LookupRecord:** Enrich a record by looking up data from another source (DB, file, etc.).
   -  **UpdateRecord:** Modify fields in a structured record flow (like JSON, CSV, Avro). Example: Change "temp" field to Celsius, or add a "processed_at" timestamp.
   - **Convert Record:** Write data to HDFS in a supported format (like Parquet or Avro).
   - **MonitorActivity:** Monitor data flow inactivity and alert if data hasn't arrived in a set time. Example: Alert if no sensor data arrives in 5 minutes.
   - **ValidateRecord:** Ensure incoming data conforms to a schema (like Avro/JSON Schema).

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