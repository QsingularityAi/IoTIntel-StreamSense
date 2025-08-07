#!/usr/bin/env python3
"""
Test script to verify the Dataflow pipeline can start properly
"""

import os
import sys
from pipeline import run_pipeline
import threading
import time

def test_pipeline_startup():
    """Test if the pipeline can start without errors"""
    
    project_id = os.getenv('PROJECT_ID', 'iotintel-streamsense')
    subscription_name = 'iot-data-subscription'
    dataset_id = 'iot_data'
    table_id = 'sensor_readings'
    
    print(f"🧪 Testing Dataflow pipeline startup...")
    print(f"   Project: {project_id}")
    print(f"   Subscription: {subscription_name}")
    print(f"   Dataset: {dataset_id}")
    print(f"   Table: {table_id}")
    
    def run_pipeline_thread():
        """Run pipeline in a separate thread"""
        try:
            run_pipeline(project_id, subscription_name, dataset_id, table_id)
        except Exception as e:
            print(f"❌ Pipeline error: {e}")
            import traceback
            traceback.print_exc()
    
    # Start pipeline in a thread
    pipeline_thread = threading.Thread(target=run_pipeline_thread, daemon=True)
    pipeline_thread.start()
    
    # Wait a few seconds to see if it starts successfully
    time.sleep(5)
    
    if pipeline_thread.is_alive():
        print("✅ Pipeline started successfully and is running")
        print("   (Pipeline would continue running to process messages)")
        return True
    else:
        print("❌ Pipeline thread exited unexpectedly")
        return False

if __name__ == '__main__':
    success = test_pipeline_startup()
    print(f"\n🎯 Pipeline test result: {'PASS' if success else 'FAIL'}")
    sys.exit(0 if success else 1)