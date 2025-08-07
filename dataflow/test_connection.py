#!/usr/bin/env python3
"""
Test script to verify GCP connection and project access
"""

import os
from google.cloud import pubsub_v1
from google.cloud import bigquery
import sys

def test_project_access():
    """Test if we can access the GCP project"""
    
    project_id = os.getenv('PROJECT_ID', 'zeltask-staging-464722')
    print(f"Testing access to project: {project_id}")
    
    # Test BigQuery access
    try:
        bq_client = bigquery.Client(project=project_id)
        datasets = list(bq_client.list_datasets())
        print(f"✅ BigQuery access OK - Found {len(datasets)} datasets")
        
        # Check if our dataset exists
        try:
            dataset = bq_client.get_dataset('iot_data')
            print(f"✅ Dataset 'iot_data' exists")
        except Exception as e:
            print(f"⚠️ Dataset 'iot_data' not found: {e}")
            
    except Exception as e:
        print(f"❌ BigQuery access failed: {e}")
        return False
    
    # Test Pub/Sub access
    try:
        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = subscriber.subscription_path(project_id, 'iot-data-subscription')
        
        # Try to get subscription info
        subscription = subscriber.get_subscription(request={"subscription": subscription_path})
        print(f"✅ Pub/Sub access OK - Subscription exists: {subscription.name}")
        
    except Exception as e:
        print(f"❌ Pub/Sub access failed: {e}")
        return False
    
    print("✅ All GCP services accessible!")
    return True

if __name__ == '__main__':
    success = test_project_access()
    sys.exit(0 if success else 1)