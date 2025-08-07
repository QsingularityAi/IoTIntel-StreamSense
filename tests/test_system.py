#!/usr/bin/env python3
"""
System tests for the IoT anomaly detection system
"""

import unittest
import json
import os
from datetime import datetime
import numpy as np

class TestIoTSystem(unittest.TestCase):
    
    def test_simulator_data_generation(self):
        """Test that the simulator generates valid data"""
        # Import the simulator module
        from simulator.iot_simulator import IoTDeviceSimulator
        
        # Create a simulator instance
        simulator = IoTDeviceSimulator(
            project_id="test-project",
            topic_name="test-topic",
            num_devices=5
        )
        
        # Generate sample data
        samples = simulator.generate_sample_data(10)
        
        # Check that we have the expected number of samples
        self.assertEqual(len(samples), 10)
        
        # Check the structure of each sample
        for sample in samples:
            self.assertIn('device_id', sample)
            self.assertIn('timestamp', sample)
            self.assertIn('location', sample)
            self.assertIn('device_type', sample)
            self.assertIn('sensor_data', sample)
            self.assertIn('is_anomaly', sample)
            
            # Check sensor data structure
            sensor_data = sample['sensor_data']
            self.assertIn('temperature', sensor_data)
            self.assertIn('vibration', sensor_data)
            
            # Check that temperature and vibration are reasonable values
            self.assertGreaterEqual(sensor_data['temperature'], -50)  # Reasonable lower bound
            self.assertLessEqual(sensor_data['temperature'], 100)     # Reasonable upper bound
            self.assertGreaterEqual(sensor_data['vibration'], 0)       # Vibration can't be negative
            
    def test_consumer_data_processing(self):
        """Test that the consumer processes data correctly"""
        # Import the consumer module
        from data_consumer.consumer import IoTDataConsumer
        
        # Create a consumer instance
        consumer = IoTDataConsumer(
            project_id="test-project",
            subscription_name="test-subscription"
        )
        
        # Create a sample message
        sample_message = {
            "device_id": "sensor_0001",
            "timestamp": datetime.now().isoformat(),
            "location": {
                "building": "Building_A",
                "floor": 3,
                "room": "Room_305"
            },
            "device_type": "industrial_sensor",
            "sensor_data": {
                "temperature": 23.5,
                "vibration": 1.2
            },
            "is_anomaly": False
        }
        
        # Test preparing data for BigQuery
        bq_row = {
            "device_id": sample_message["device_id"],
            "timestamp": sample_message["timestamp"],
            "building": sample_message["location"]["building"],
            "floor": sample_message["location"]["floor"],
            "room": sample_message["location"]["room"],
            "device_type": sample_message["device_type"],
            "temperature": sample_message["sensor_data"]["temperature"],
            "vibration": sample_message["sensor_data"]["vibration"],
            "is_anomaly": sample_message["is_anomaly"]
        }
        
        # Check that all expected fields are present
        expected_fields = [
            "device_id", "timestamp", "building", "floor", 
            "room", "device_type", "temperature", "vibration", "is_anomaly"
        ]
        
        for field in expected_fields:
            self.assertIn(field, bq_row)
            
    def test_ml_trainer_feature_preparation(self):
        """Test that the ML trainer prepares features correctly"""
        # Import the trainer module
        from ml_trainer.trainer import AnomalyDetectionTrainer
        
        # Create a trainer instance
        trainer = AnomalyDetectionTrainer(project_id="test-project")
        
        # Create sample data
        sample_data = [
            {
                "device_id": "sensor_0001",
                "timestamp": datetime.now().isoformat(),
                "temperature": 23.5,
                "vibration": 1.2,
                "is_anomaly": False
            },
            {
                "device_id": "sensor_0001",
                "timestamp": datetime.now().isoformat(),
                "temperature": 24.1,
                "vibration": 1.3,
                "is_anomaly": False
            }
        ]
        
        # Convert to format expected by prepare_features
        import pandas as pd
        df = pd.DataFrame(sample_data)
        
        # Test feature preparation
        X, df_processed = trainer.prepare_features(df)
        
        # Check that features are created
        self.assertIsNotNone(X)
        self.assertIsNotNone(df_processed)
        
        # Check that time-based features are added
        self.assertIn('hour', df_processed.columns)
        self.assertIn('day_of_week', df_processed.columns)
        
        # Check that statistical features are added
        self.assertIn('temp_ma', df_processed.columns)
        self.assertIn('vibration_ma', df_processed.columns)
        self.assertIn('temp_zscore', df_processed.columns)
        self.assertIn('vibration_zscore', df_processed.columns)
        
    def test_ml_server_anomaly_detection(self):
        """Test that the ML server detects anomalies correctly"""
        # Import the server module
        from ml_server.server import prepare_features
        
        # Create sample data
        sample_data = {
            "device_id": "sensor_0001",
            "timestamp": datetime.now().isoformat(),
            "temperature": 23.5,
            "vibration": 1.2
        }
        
        # Test feature preparation
        features = prepare_features(sample_data)
        
        # Check that features are created
        self.assertIsNotNone(features)
        
        # Check that all expected features are present
        expected_features = [
            'temperature', 'vibration', 'hour', 'day_of_week', 
            'temp_ma', 'vibration_ma', 'temp_zscore', 'vibration_zscore'
        ]
        
        for feature in expected_features:
            self.assertIn(feature, features)

if __name__ == '__main__':
    unittest.main()
