#!/usr/bin/env python3
"""
Setup script for Pub/Sub emulator
Creates the required topics and subscriptions for the IoT project
"""

import os
import time
from google.cloud import pubsub_v1

def setup_pubsub():
    # Set the emulator host
    os.environ['PUBSUB_EMULATOR_HOST'] = 'localhost:8085'
    
    # Configuration
    project_id = "iotintel-streamsense"
    topic_name = "iot-temp-vibration-data" 
    subscription_name = "iot-temp-vibration-subscription"
    
    print(f"Setting up Pub/Sub emulator for project: {project_id}")
    print(f"Creating topic: {topic_name}")
    print(f"Creating subscription: {subscription_name}")
    
    # Create publisher and subscriber clients
    publisher = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()
    
    # Create topic path
    topic_path = publisher.topic_path(project_id, topic_name)
    subscription_path = subscriber.subscription_path(project_id, subscription_name)
    
    try:
        # Create topic
        topic = publisher.create_topic(request={"name": topic_path})
        print(f"Created topic: {topic.name}")
    except Exception as e:
        print(f"Topic might already exist: {e}")
    
    try:
        # Create subscription
        subscription = subscriber.create_subscription(
            request={"name": subscription_path, "topic": topic_path}
        )
        print(f"Created subscription: {subscription.name}")
    except Exception as e:
        print(f"Subscription might already exist: {e}")
    
    print("Pub/Sub setup complete!")

if __name__ == "__main__":
    # Wait a bit for the emulator to be fully ready
    time.sleep(2)
    setup_pubsub()
