#!/usr/bin/env python3
"""
Test Pub/Sub publishing to Google Cloud
"""

import os
import json
from google.cloud import pubsub_v1

def test_publish():
    project_id = 'zeltask-staging-464722'
    topic_name = 'iot-temp-vibration-data'
    
    print(f"Testing Pub/Sub publishing to Google Cloud...")
    print(f"Project ID: {project_id}")
    print(f"Topic: {topic_name}")
    print(f"Credentials: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
    
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)
    
    test_data = json.dumps({'test': 'message', 'timestamp': '2024-01-01T00:00:00'}).encode('utf-8')
    
    try:
        future = publisher.publish(topic_path, test_data)
        message_id = future.result(timeout=10)
        print(f"SUCCESS: Published message to Google Cloud with ID: {message_id}")
        return True
    except Exception as e:
        print(f"ERROR publishing message: {e}")
        return False

if __name__ == "__main__":
    test_publish()
