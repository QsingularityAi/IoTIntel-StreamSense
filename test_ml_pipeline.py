#!/usr/bin/env python3
"""
Test script to demonstrate the complete ML pipeline
"""

import requests
import json
import time
from datetime import datetime

# Configuration
ML_SERVER_URL = "http://localhost:8000"

def test_ml_predictions():
    """Test various ML predictions"""
    
    print("🤖 Testing IoT ML Anomaly Detection Pipeline")
    print("=" * 50)
    
    # Test cases: [temperature, vibration, expected_anomaly_description]
    test_cases = [
        [20.5, 1.0, "Normal readings"],
        [35.0, 1.2, "High temperature anomaly"],
        [21.0, 4.5, "High vibration anomaly"],
        [15.0, 5.0, "Both temperature and vibration anomalies"],
        [22.0, 0.8, "Normal readings"],
        [28.0, 2.5, "Possible anomalies"]
    ]
    
    print(f"Testing {len(test_cases)} scenarios...\n")
    
    for i, (temp, vib, description) in enumerate(test_cases, 1):
        print(f"Test {i}: {description}")
        print(f"Input: Temperature={temp}°C, Vibration={vib}mm/s")
        
        # Prepare request data
        data = {
            "device_id": f"test_device_{i}",
            "timestamp": datetime.now().isoformat(),
            "temperature": temp,
            "vibration": vib
        }
        
        try:
            # Make prediction request
            response = requests.post(f"{ML_SERVER_URL}/detect", json=data, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                
                # Display results
                temp_status = "🚨 ANOMALY" if result.get('is_temp_anomaly') else "✅ NORMAL"
                vib_status = "🚨 ANOMALY" if result.get('is_vibration_anomaly') else "✅ NORMAL"
                overall_status = "🚨 ANOMALY DETECTED" if result.get('is_anomaly') else "✅ ALL NORMAL"
                
                print(f"Results:")
                print(f"  Temperature: {temp_status} (score: {result.get('temp_anomaly_score', 0):.4f})")
                print(f"  Vibration:   {vib_status} (score: {result.get('vibration_anomaly_score', 0):.4f})")
                print(f"  Overall:     {overall_status}")
                
            else:
                print(f"❌ Request failed with status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)
        time.sleep(0.5)  # Small delay between requests
    
    print("\n🎯 ML Pipeline Test Complete!")
    print("\nTo view real-time predictions:")
    print("1. Open http://localhost:8501 (Streamlit Dashboard)")
    print("2. Use the ML Prediction Demo in the sidebar")
    print("3. Adjust temperature and vibration sliders")
    print("4. Click 'Get ML Prediction' to see results")

def test_model_performance():
    """Display model performance information"""
    print("\n📊 Model Performance Summary")
    print("=" * 30)
    
    # This would typically load from the metrics files
    print("Temperature Model:")
    print("  - Trained on 54,559 records")
    print("  - Isolation Forest algorithm")
    print("  - Features: temperature, hour, day_of_week, moving_avg, z_score")
    print("  - Contamination rate: 10%")
    
    print("\nVibration Model:")
    print("  - Trained on 54,559 records") 
    print("  - Isolation Forest algorithm")
    print("  - Features: vibration, hour, day_of_week, moving_avg, z_score")
    print("  - Contamination rate: 10%")
    
    print("\nNote: Models are unsupervised (Isolation Forest)")
    print("They detect outliers based on feature distributions")
    print("Lower anomaly scores indicate higher anomaly likelihood")

if __name__ == "__main__":
    print("🏭 IoT Anomaly Detection System - ML Pipeline Test")
    print("=" * 60)
    
    # Test model performance info
    test_model_performance()
    
    # Test ML predictions
    test_ml_predictions()