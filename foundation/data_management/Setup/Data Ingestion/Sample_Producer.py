from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime

# kafka_ip = 'kafka'
kafka_ip = '172.18.0.6'


producer = KafkaProducer(
    bootstrap_servers= kafka_ip + ':9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

while True:
    data = {
        "source": f"sensor{random.randint(1, 5)}",
        "temp": round(random.uniform(25, 35), 2),
        "timestamp": datetime.utcnow().isoformat()
    }
    producer.send('temp_producer', value=data)
    print(f"Sent: {data}")
    time.sleep(2)  # Send a message every 2 seconds


# Create a virtual environment
# python -m venv kafka-env

# Activate it
# source kafka-env/bin/activate  # macOS/Linux

# Install latest kafka-python
# pip install kafka-python==2.0.2

# Exit environment
# deactivate
