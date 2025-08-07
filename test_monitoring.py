#!/usr/bin/env python3
"""
Test script to verify Grafana and Prometheus monitoring setup
"""

import requests
import time
import json
import sys
from datetime import datetime

def test_prometheus():
    """Test Prometheus connectivity and metrics"""
    print("🔍 Testing Prometheus...")
    
    try:
        # Test Prometheus health
        response = requests.get("http://localhost:9090/-/healthy", timeout=10)
        if response.status_code == 200:
            print("✅ Prometheus is healthy")
        else:
            print(f"❌ Prometheus health check failed: {response.status_code}")
            return False
        
        # Test metrics endpoint
        response = requests.get("http://localhost:9090/api/v1/query?query=up", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                print(f"✅ Prometheus metrics available: {len(data['data']['result'])} targets")
                
                # Show target status
                for result in data['data']['result']:
                    job = result['metric'].get('job', 'unknown')
                    instance = result['metric'].get('instance', 'unknown')
                    value = result['value'][1]
                    status = "UP" if value == "1" else "DOWN"
                    print(f"   📊 {job} ({instance}): {status}")
            else:
                print("❌ Prometheus query failed")
                return False
        else:
            print(f"❌ Prometheus metrics query failed: {response.status_code}")
            return False
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Prometheus connection failed: {e}")
        return False

def test_grafana():
    """Test Grafana connectivity and dashboards"""
    print("\n🎨 Testing Grafana...")
    
    try:
        # Test Grafana health
        response = requests.get("http://localhost:3000/api/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Grafana is healthy: {health_data.get('database', 'unknown')} database")
        else:
            print(f"❌ Grafana health check failed: {response.status_code}")
            return False
        
        # Test datasources
        response = requests.get(
            "http://localhost:3000/api/datasources", 
            auth=('admin', 'admin'),
            timeout=10
        )
        if response.status_code == 200:
            datasources = response.json()
            print(f"✅ Grafana datasources configured: {len(datasources)} datasources")
            for ds in datasources:
                print(f"   📊 {ds['name']} ({ds['type']}): {ds['url']}")
        else:
            print(f"❌ Grafana datasources check failed: {response.status_code}")
            return False
        
        # Test dashboards
        response = requests.get(
            "http://localhost:3000/api/search", 
            auth=('admin', 'admin'),
            timeout=10
        )
        if response.status_code == 200:
            dashboards = response.json()
            print(f"✅ Grafana dashboards available: {len(dashboards)} dashboards")
            for dashboard in dashboards:
                print(f"   📈 {dashboard['title']} (UID: {dashboard['uid']})")
        else:
            print(f"❌ Grafana dashboards check failed: {response.status_code}")
            return False
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Grafana connection failed: {e}")
        return False

def test_alertmanager():
    """Test Alertmanager connectivity"""
    print("\n🚨 Testing Alertmanager...")
    
    try:
        # Test Alertmanager health
        response = requests.get("http://localhost:9093/-/healthy", timeout=10)
        if response.status_code == 200:
            print("✅ Alertmanager is healthy")
        else:
            print(f"❌ Alertmanager health check failed: {response.status_code}")
            return False
        
        # Test alerts endpoint
        response = requests.get("http://localhost:9093/api/v1/alerts", timeout=10)
        if response.status_code == 200:
            alerts = response.json()
            print(f"✅ Alertmanager alerts endpoint accessible: {len(alerts['data'])} alerts")
        else:
            print(f"❌ Alertmanager alerts check failed: {response.status_code}")
            return False
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Alertmanager connection failed: {e}")
        return False

def test_ml_server_metrics():
    """Test ML Server metrics endpoint"""
    print("\n🤖 Testing ML Server Metrics...")
    
    try:
        # Test ML Server health
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ ML Server is healthy")
        else:
            print(f"❌ ML Server health check failed: {response.status_code}")
            return False
        
        # Test metrics endpoint
        response = requests.get("http://localhost:8000/metrics", timeout=10)
        if response.status_code == 200:
            metrics_text = response.text
            print("✅ ML Server metrics endpoint accessible")
            
            # Count metrics
            metric_lines = [line for line in metrics_text.split('\n') if line and not line.startswith('#')]
            print(f"   📊 Available metrics: {len(metric_lines)} metric values")
            
            # Show some key metrics
            key_metrics = ['ml_predictions_total', 'ml_anomalies_detected_total', 'http_requests_total']
            for metric in key_metrics:
                if metric in metrics_text:
                    print(f"   ✅ {metric} metric available")
                else:
                    print(f"   ⚠️ {metric} metric not found")
        else:
            print(f"❌ ML Server metrics check failed: {response.status_code}")
            return False
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ ML Server connection failed: {e}")
        return False

def test_node_exporter():
    """Test Node Exporter metrics"""
    print("\n💻 Testing Node Exporter...")
    
    try:
        response = requests.get("http://localhost:9100/metrics", timeout=10)
        if response.status_code == 200:
            metrics_text = response.text
            print("✅ Node Exporter metrics accessible")
            
            # Check for key system metrics
            key_metrics = ['node_cpu_seconds_total', 'node_memory_MemTotal_bytes', 'node_filesystem_size_bytes']
            for metric in key_metrics:
                if metric in metrics_text:
                    print(f"   ✅ {metric} available")
                else:
                    print(f"   ⚠️ {metric} not found")
        else:
            print(f"❌ Node Exporter check failed: {response.status_code}")
            return False
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Node Exporter connection failed: {e}")
        return False

def test_cadvisor():
    """Test cAdvisor container metrics"""
    print("\n🐳 Testing cAdvisor...")
    
    try:
        response = requests.get("http://localhost:8080/metrics", timeout=10)
        if response.status_code == 200:
            metrics_text = response.text
            print("✅ cAdvisor metrics accessible")
            
            # Check for container metrics
            key_metrics = ['container_cpu_usage_seconds_total', 'container_memory_usage_bytes']
            for metric in key_metrics:
                if metric in metrics_text:
                    print(f"   ✅ {metric} available")
                else:
                    print(f"   ⚠️ {metric} not found")
        else:
            print(f"❌ cAdvisor check failed: {response.status_code}")
            return False
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ cAdvisor connection failed: {e}")
        return False

def generate_test_metrics():
    """Generate some test metrics by making ML predictions"""
    print("\n🧪 Generating test metrics...")
    
    try:
        # Make some test predictions to generate metrics
        test_data = [
            {"device_id": "test_device_1", "temperature": 22.5, "vibration": 1.2},
            {"device_id": "test_device_2", "temperature": 35.0, "vibration": 1.5},  # Should be anomaly
            {"device_id": "test_device_3", "temperature": 21.0, "vibration": 4.5},  # Should be anomaly
            {"device_id": "test_device_4", "temperature": 20.0, "vibration": 1.0},
            {"device_id": "test_device_5", "temperature": 15.0, "vibration": 5.0},  # Should be anomaly
        ]
        
        predictions_made = 0
        anomalies_detected = 0
        
        for data in test_data:
            response = requests.post(
                "http://localhost:8000/detect",
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                predictions_made += 1
                if result.get('is_anomaly'):
                    anomalies_detected += 1
                    print(f"   🚨 Anomaly detected for {data['device_id']}")
                else:
                    print(f"   ✅ Normal reading for {data['device_id']}")
            else:
                print(f"   ❌ Prediction failed for {data['device_id']}")
        
        print(f"✅ Generated {predictions_made} predictions, {anomalies_detected} anomalies detected")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to generate test metrics: {e}")
        return False

def main():
    """Run all monitoring tests"""
    print("🔍 IoT ML System Monitoring Test Suite")
    print("=" * 50)
    
    tests = [
        ("Prometheus", test_prometheus),
        ("Grafana", test_grafana),
        ("Alertmanager", test_alertmanager),
        ("ML Server Metrics", test_ml_server_metrics),
        ("Node Exporter", test_node_exporter),
        ("cAdvisor", test_cadvisor),
        ("Generate Test Metrics", generate_test_metrics),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False
        
        time.sleep(1)  # Small delay between tests
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All monitoring components are working perfectly!")
        print("\n🔗 Access URLs:")
        print("   Grafana Dashboard: http://localhost:3000 (admin/admin)")
        print("   Prometheus: http://localhost:9090")
        print("   Alertmanager: http://localhost:9093")
        print("   Node Exporter: http://localhost:9100")
        print("   cAdvisor: http://localhost:8080")
        print("   ML Server: http://localhost:8000")
        return 0
    else:
        print("⚠️ Some monitoring components need attention.")
        print("Please check the failed tests and ensure all services are running.")
        return 1

if __name__ == "__main__":
    sys.exit(main())