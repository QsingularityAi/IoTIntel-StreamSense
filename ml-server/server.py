#!/usr/bin/env python3
"""
IoT Anomaly Detection ML Server
Serves trained machine learning models via REST API for real-time anomaly detection.
"""

import flask
from flask import Flask, request, jsonify
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
import logging
from datetime import datetime
import os
import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# FastAPI app
fastapi_app = FastAPI()

# Global variables for models and scalers
temp_model = None
temp_scaler = None
vibration_model = None
vibration_scaler = None

# Prometheus metrics
ml_predictions_total = Counter('ml_predictions_total', 'Total number of ML predictions made')
ml_predictions_success_total = Counter('ml_predictions_success_total', 'Total number of successful ML predictions')
ml_anomalies_detected_total = Counter('ml_anomalies_detected_total', 'Total number of anomalies detected')
ml_temperature_anomalies_total = Counter('ml_temperature_anomalies_total', 'Total temperature anomalies detected')
ml_vibration_anomalies_total = Counter('ml_vibration_anomalies_total', 'Total vibration anomalies detected')
ml_prediction_duration = Histogram('ml_prediction_duration_seconds', 'Time spent on ML predictions')
ml_model_accuracy = Gauge('ml_model_accuracy', 'Current model accuracy', ['model_type'])
http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
http_request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

def load_models():
    """Load trained models and scalers"""
    global temp_model, temp_scaler, vibration_model, vibration_scaler
    
    try:
        temp_model = joblib.load("./ml-models/temperature_model.pkl")
        temp_scaler = joblib.load("./ml-models/temperature_scaler.pkl")
        vibration_model = joblib.load("./ml-models/vibration_model.pkl")
        vibration_scaler = joblib.load("./ml-models/vibration_scaler.pkl")
        logger.info("Models loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        return False

def prepare_features(data):
    """Prepare features for anomaly detection"""
    try:
        # Convert timestamp to datetime
        timestamp = pd.to_datetime(data.get('timestamp', datetime.now()))
        
        # Extract time-based features
        hour = timestamp.hour
        day_of_week = timestamp.dayofweek
        
        # Get sensor data
        temperature = data.get('temperature', 0)
        vibration = data.get('vibration', 0)
        
        # For simplicity, we're not calculating moving averages or z-scores here
        # In a production system, these would be calculated based on historical data
        temp_ma = temperature
        vibration_ma = vibration
        temp_zscore = 0
        vibration_zscore = 0
        
        return {
            'temperature': temperature,
            'vibration': vibration,
            'hour': hour,
            'day_of_week': day_of_week,
            'temp_ma': temp_ma,
            'vibration_ma': vibration_ma,
            'temp_zscore': temp_zscore,
            'vibration_zscore': vibration_zscore
        }
    except Exception as e:
        logger.error(f"Error preparing features: {e}")
        return None

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    start_time = time.time()
    try:
        result = {"status": "healthy", "timestamp": datetime.now().isoformat()}
        http_requests_total.labels(method='GET', endpoint='/health', status='200').inc()
        return jsonify(result)
    finally:
        http_request_duration.observe(time.time() - start_time)

@app.route('/detect/temperature', methods=['POST'])
def detect_temperature_anomaly():
    """Detect temperature anomalies"""
    start_time = time.time()
    try:
        ml_predictions_total.inc()
        
        data = request.get_json()
        
        if not data:
            http_requests_total.labels(method='POST', endpoint='/detect/temperature', status='400').inc()
            return jsonify({"error": "No data provided"}), 400
        
        with ml_prediction_duration.time():
            # Prepare features
            features = prepare_features(data)
            if not features:
                http_requests_total.labels(method='POST', endpoint='/detect/temperature', status='500').inc()
                return jsonify({"error": "Failed to prepare features"}), 500
            
            # Select temperature features
            temp_features = ['temperature', 'hour', 'day_of_week', 'temp_ma', 'temp_zscore']
            X = np.array([[features[f] for f in temp_features]])
            
            # Scale features
            X_scaled = temp_scaler.transform(X)
            
            # Predict anomaly
            anomaly_score = temp_model.decision_function(X_scaled)[0]
            is_anomaly = temp_model.predict(X_scaled)[0] == -1  # Isolation Forest returns -1 for anomalies
        
        if is_anomaly:
            ml_anomalies_detected_total.inc()
            ml_temperature_anomalies_total.inc()
        
        result = {
            "device_id": data.get('device_id', 'unknown'),
            "timestamp": data.get('timestamp', datetime.now().isoformat()),
            "temperature": features['temperature'],
            "anomaly_score": float(anomaly_score),
            "is_anomaly": bool(is_anomaly)
        }
        
        ml_predictions_success_total.inc()
        http_requests_total.labels(method='POST', endpoint='/detect/temperature', status='200').inc()
        logger.info(f"Temperature anomaly detection for device {result['device_id']}: {result['is_anomaly']}")
        return jsonify(result)
        
    except Exception as e:
        http_requests_total.labels(method='POST', endpoint='/detect/temperature', status='500').inc()
        logger.error(f"Error in temperature anomaly detection: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        http_request_duration.observe(time.time() - start_time)

@app.route('/detect/vibration', methods=['POST'])
def detect_vibration_anomaly():
    """Detect vibration anomalies"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Prepare features
        features = prepare_features(data)
        if not features:
            return jsonify({"error": "Failed to prepare features"}), 500
        
        # Select vibration features
        vibration_features = ['vibration', 'hour', 'day_of_week', 'vibration_ma', 'vibration_zscore']
        X = np.array([[features[f] for f in vibration_features]])
        
        # Scale features
        X_scaled = vibration_scaler.transform(X)
        
        # Predict anomaly
        anomaly_score = vibration_model.decision_function(X_scaled)[0]
        is_anomaly = vibration_model.predict(X_scaled)[0] == -1  # Isolation Forest returns -1 for anomalies
        
        result = {
            "device_id": data.get('device_id', 'unknown'),
            "timestamp": data.get('timestamp', datetime.now().isoformat()),
            "vibration": features['vibration'],
            "anomaly_score": float(anomaly_score),
            "is_anomaly": bool(is_anomaly)
        }
        
        logger.info(f"Vibration anomaly detection for device {result['device_id']}: {result['is_anomaly']}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in vibration anomaly detection: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/detect', methods=['POST'])
def detect_anomalies():
    """Detect both temperature and vibration anomalies"""
    start_time = time.time()
    try:
        # Check if models are loaded
        if temp_model is None or vibration_model is None:
            logger.error("Models not loaded!")
            return jsonify({"error": "Models not loaded"}), 500
            
        ml_predictions_total.inc()
        logger.info(f"Incremented ml_predictions_total to {ml_predictions_total._value._value}")
        
        data = request.get_json()
        
        if not data:
            http_requests_total.labels(method='POST', endpoint='/detect', status='400').inc()
            return jsonify({"error": "No data provided"}), 400
        
        with ml_prediction_duration.time():
            # Prepare features
            features = prepare_features(data)
            if not features:
                http_requests_total.labels(method='POST', endpoint='/detect', status='500').inc()
                return jsonify({"error": "Failed to prepare features"}), 500
            
            # Temperature anomaly detection
            temp_features = ['temperature', 'hour', 'day_of_week', 'temp_ma', 'temp_zscore']
            X_temp = np.array([[features[f] for f in temp_features]])
            X_temp_scaled = temp_scaler.transform(X_temp)
            temp_anomaly_score = temp_model.decision_function(X_temp_scaled)[0]
            is_temp_anomaly = temp_model.predict(X_temp_scaled)[0] == -1
            
            # Vibration anomaly detection
            vibration_features = ['vibration', 'hour', 'day_of_week', 'vibration_ma', 'vibration_zscore']
            X_vibration = np.array([[features[f] for f in vibration_features]])
            X_vibration_scaled = vibration_scaler.transform(X_vibration)
            vibration_anomaly_score = vibration_model.decision_function(X_vibration_scaled)[0]
            is_vibration_anomaly = vibration_model.predict(X_vibration_scaled)[0] == -1
        
        # Update metrics
        if is_temp_anomaly or is_vibration_anomaly:
            ml_anomalies_detected_total.inc()
            logger.info(f"Incremented ml_anomalies_detected_total to {ml_anomalies_detected_total._value._value}")
        if is_temp_anomaly:
            ml_temperature_anomalies_total.inc()
            logger.info(f"Incremented ml_temperature_anomalies_total to {ml_temperature_anomalies_total._value._value}")
        if is_vibration_anomaly:
            ml_vibration_anomalies_total.inc()
            logger.info(f"Incremented ml_vibration_anomalies_total to {ml_vibration_anomalies_total._value._value}")
        
        result = {
            "device_id": data.get('device_id', 'unknown'),
            "timestamp": data.get('timestamp', datetime.now().isoformat()),
            "temperature": features['temperature'],
            "vibration": features['vibration'],
            "temp_anomaly_score": float(temp_anomaly_score),
            "vibration_anomaly_score": float(vibration_anomaly_score),
            "is_temp_anomaly": bool(is_temp_anomaly),
            "is_vibration_anomaly": bool(is_vibration_anomaly),
            "is_anomaly": bool(is_temp_anomaly or is_vibration_anomaly)
        }
        
        ml_predictions_success_total.inc()
        http_requests_total.labels(method='POST', endpoint='/detect', status='200').inc()
        logger.info(f"Anomaly detection for device {result['device_id']}: temp={result['is_temp_anomaly']}, vibration={result['is_vibration_anomaly']}")
        return jsonify(result)
        
    except Exception as e:
        http_requests_total.labels(method='POST', endpoint='/detect', status='500').inc()
        logger.error(f"Error in anomaly detection: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        http_request_duration.observe(time.time() - start_time)

@app.route('/alert', methods=['POST'])
def create_alert():
    """Create an alert for detected anomalies"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # In a production system, this would send alerts via email, SMS, or other channels
        # For now, we'll just log the alert
        alert_message = {
            "device_id": data.get('device_id', 'unknown'),
            "timestamp": data.get('timestamp', datetime.now().isoformat()),
            "alert_type": data.get('alert_type', 'unknown'),
            "severity": data.get('severity', 'medium'),
            "message": data.get('message', ''),
            "temperature": data.get('temperature'),
            "vibration": data.get('vibration')
        }
        
        logger.warning(f"ALERT: {alert_message}")
        
        # Return success response
        return jsonify({"status": "alert created", "alert": alert_message})
        
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        return jsonify({"error": "Internal server error"}), 500

# FastAPI routes

class PredictionRequest(BaseModel):
    temperature: float
    vibration: float
    hour: int
    day_of_week: int
    temp_ma: float
    vibration_ma: float
    temp_zscore: float
    vibration_zscore: float

@fastapi_app.post("/predict")
def predict(req: PredictionRequest):
    # Prepare features for each model
    temp_features = np.array([[req.temperature, req.hour, req.day_of_week, req.temp_ma, req.temp_zscore]])
    vib_features = np.array([[req.vibration, req.hour, req.day_of_week, req.vibration_ma, req.vibration_zscore]])
    temp_scaled = temp_scaler.transform(temp_features)
    vib_scaled = vibration_scaler.transform(vib_features)
    temp_pred = temp_model.predict(temp_scaled)[0]
    vib_pred = vibration_model.predict(vib_scaled)[0]
    # IsolationForest: -1 = anomaly, 1 = normal
    result = {
        "temperature_anomaly": temp_pred == -1,
        "vibration_anomaly": vib_pred == -1
    }
    logger.info(f"Prediction: {result}")
    return result

@fastapi_app.get("/")
def root():
    return {"status": "Model server is running"}

if __name__ == '__main__':
    # Load models
    if not load_models():
        logger.error("Failed to load models, exiting...")
        exit(1)
    
    # Run the server
    app.run(host='0.0.0.0', port=8000, debug=False)
