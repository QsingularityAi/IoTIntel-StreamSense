#!/usr/bin/env python3
"""
IoT Data Consumer - Processes messages from Pub/Sub
Consumes temperature and vibration sensor data and stores it in BigQuery.
"""

import json
import logging
import os
from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1, bigquery
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IoTDataConsumer:
    def __init__(self, project_id, subscription_name):
        self.project_id = project_id
        self.subscription_name = subscription_name
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(project_id, subscription_name)
        self.bq_client = bigquery.Client(project=project_id)
        self.dataset_id = "iot_data"
        self.table_id = "sensor_readings"
        
    def process_message(self, message):
        """Process a single Pub/Sub message"""
        try:
            # Decode and parse the message
            data = json.loads(message.data.decode('utf-8'))
            logger.info(f"Received message from device {data['device_id']}")
            
            # Prepare data for BigQuery
            bq_row = {
                "device_id": data["device_id"],
                "timestamp": data["timestamp"],
                "building": data["location"]["building"],
                "floor": data["location"]["floor"],
                "room": data["location"]["room"],
                "device_type": data["device_type"],
                "temperature": data["sensor_data"]["temperature"],
                "vibration": data["sensor_data"]["vibration"],
                "is_anomaly": data["is_anomaly"]
            }
            
            # Add anomaly type if present
            if "anomaly_type" in data["sensor_data"]:
                bq_row["anomaly_type"] = data["sensor_data"]["anomaly_type"]
            
            # Insert into BigQuery
            self.insert_into_bigquery(bq_row)
            
            # Acknowledge the message
            message.ack()
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            message.nack()
    
    def insert_into_bigquery(self, row):
        """Insert a row into BigQuery"""
        try:
            table_ref = self.bq_client.dataset(self.dataset_id).table(self.table_id)
            table = self.bq_client.get_table(table_ref)
            
            errors = self.bq_client.insert_rows_json(table, [row])
            if errors:
                logger.error(f"BigQuery insert errors: {errors}")
            else:
                logger.info(f"Successfully inserted row for device {row['device_id']}")
                
        except Exception as e:
            logger.error(f"Error inserting into BigQuery: {e}")
    
    def listen_for_messages(self):
        """Listen for messages from Pub/Sub subscription"""
        streaming_pull_future = self.subscriber.subscribe(self.subscription_path, callback=self.process_message)
        logger.info(f"Listening for messages on {self.subscription_path}")
        
        # Wrap subscriber in a 'with' block to automatically close
        with self.subscriber:
            try:
                # When timeout is not set, result() will block indefinitely,
                # unless an exception is encountered first.
                streaming_pull_future.result()
            except TimeoutError:
                streaming_pull_future.cancel()  # Trigger the shutdown
                streaming_pull_future.result()  # Block until the shutdown is complete
            except Exception as e:
                logger.error(f"Error in message listener: {e}")
                streaming_pull_future.cancel()
                streaming_pull_future.result()

def main():
    # Configuration - get from environment variables or use defaults
    PROJECT_ID = os.getenv("PROJECT_ID", "iotintel-streamsense")  # Use the correct project ID
    SUBSCRIPTION_NAME = os.getenv("SUBSCRIPTION_NAME", "iot-data-subscription")
    
    # Create consumer
    consumer = IoTDataConsumer(
        project_id=PROJECT_ID,
        subscription_name=SUBSCRIPTION_NAME
    )
    
    # Start listening for messages
    consumer.listen_for_messages()

if __name__ == "__main__":
    main()
