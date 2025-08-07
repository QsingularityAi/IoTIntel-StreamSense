#!/usr/bin/env python3
"""
Quick script to generate test data for the ML Performance Dashboard
"""

import requests
import time
import random

def generate_test_data():
    """Generate diverse test data to populate metrics"""
    
    test_scenarios = [
        # Normal readings
        {'device_id': 'sensor_001', 'temperature': 21.5, 'vibration': 1.1},
        {'device_id': 'sensor_002', 'temperature': 22.0, 'vibration': 1.0},
        {'device_id': 'sensor_003', 'temperature': 20.5, 'vibration': 1.2},
        {'device_id': 'sensor_004', 'temperature': 23.0, 'vibration': 0.9},
        {'device_id': 'sensor_005', 'temperature': 21.8, 'vibration': 1.3},
        
        # Temperature anomalies
        {'device_id': 'sensor_006', 'temperature': 35.0, 'vibration': 1.1},
        {'device_id': 'sensor_007', 'temperature': 40.0, 'vibration': 1.0},
        {'device_id': 'sensor_008', 'temperature': 15.0, 'vibration': 1.2},
        {'device_id': 'sensor_009', 'temperature': 42.0, 'vibration': 1.1},
        
        # Vibration anomalies
        {'device_id': 'sensor_010', 'temperature': 22.0, 'vibration': 4.5},
        {'device_id': 'sensor_011', 'temperature': 21.0, 'vibration': 5.0},
        {'device_id': 'sensor_012', 'temperature': 23.0, 'vibration': 3.8},
        {'device_id': 'sensor_013', 'temperature': 20.5, 'vibration': 4.2},
        
        # Combined anomalies
        {'device_id': 'sensor_014', 'temperature': 38.0, 'vibration': 4.2},
        {'device_id': 'sensor_015', 'temperature': 16.0, 'vibration': 4.8},
        
        # More normal readings for balance
        {'device_id': 'sensor_016', 'temperature': 22.5, 'vibration': 1.0},
        {'device_id': 'sensor_017', 'temperature': 21.2, 'vibration': 1.1},
        {'device_id': 'sensor_018', 'temperature': 23.1, 'vibration': 0.8},
        {'device_id': 'sensor_019', 'temperature': 20.8, 'vibration': 1.4},
        {'device_id': 'sensor_020', 'temperature': 22.8, 'vibration': 1.2},
    ]
    
    print('🚀 Generating comprehensive test data for dashboard...')
    print(f'📊 Will generate {len(test_scenarios)} predictions')
    
    total_predictions = 0
    total_anomalies = 0
    temp_anomalies = 0
    vib_anomalies = 0
    combined_anomalies = 0
    
    for i, data in enumerate(test_scenarios):
        try:
            response = requests.post('http://localhost:8000/detect', json=data, timeout=5)
            if response.status_code == 200:
                result = response.json()
                total_predictions += 1
                
                if result.get('is_anomaly'):
                    total_anomalies += 1
                    
                    if result.get('is_temp_anomaly') and result.get('is_vibration_anomaly'):
                        combined_anomalies += 1
                        status = '🚨 ANOMALY (TEMP + VIB)'
                    elif result.get('is_temp_anomaly'):
                        temp_anomalies += 1
                        status = '🚨 ANOMALY (TEMP)'
                    else:
                        vib_anomalies += 1
                        status = '🚨 ANOMALY (VIB)'
                else:
                    status = '✅ NORMAL'
                
                print(f'{i+1:2d}. {data["device_id"]}: {status}')
            else:
                print(f'{i+1:2d}. {data["device_id"]}: ❌ ERROR {response.status_code}')
                
            time.sleep(0.05)  # Small delay to avoid overwhelming the server
            
        except Exception as e:
            print(f'{i+1:2d}. {data["device_id"]}: ❌ Error: {e}')
    
    print(f'\n📊 Final Summary:')
    print(f'   Total Predictions: {total_predictions}')
    print(f'   Total Anomalies: {total_anomalies} ({total_anomalies/total_predictions*100:.1f}%)')
    print(f'   Temperature Anomalies: {temp_anomalies}')
    print(f'   Vibration Anomalies: {vib_anomalies}')
    print(f'   Combined Anomalies: {combined_anomalies}')
    print('✅ Dashboard data populated!')
    
    return total_predictions, total_anomalies

def check_metrics():
    """Check current metrics values"""
    try:
        response = requests.get('http://localhost:8000/metrics', timeout=5)
        if response.status_code == 200:
            metrics_text = response.text
            
            # Extract key metrics
            for line in metrics_text.split('\n'):
                if line.startswith('ml_predictions_total '):
                    predictions = float(line.split()[1])
                    print(f'📈 Total Predictions: {predictions}')
                elif line.startswith('ml_anomalies_detected_total '):
                    anomalies = float(line.split()[1])
                    print(f'🚨 Total Anomalies: {anomalies}')
                elif line.startswith('ml_temperature_anomalies_total '):
                    temp_anomalies = float(line.split()[1])
                    print(f'🌡️  Temperature Anomalies: {temp_anomalies}')
                elif line.startswith('ml_vibration_anomalies_total '):
                    vib_anomalies = float(line.split()[1])
                    print(f'📳 Vibration Anomalies: {vib_anomalies}')
        else:
            print(f'❌ Failed to get metrics: {response.status_code}')
    except Exception as e:
        print(f'❌ Error getting metrics: {e}')

if __name__ == '__main__':
    print('🔍 Current Metrics:')
    check_metrics()
    print('\n' + '='*50)
    
    # Generate test data
    generate_test_data()
    
    print('\n' + '='*50)
    print('🔍 Updated Metrics:')
    check_metrics()
    
    print('\n🎯 Dashboard should now show data!')
    print('   Open: http://localhost:3000')
    print('   Navigate to: ML Performance Dashboard')