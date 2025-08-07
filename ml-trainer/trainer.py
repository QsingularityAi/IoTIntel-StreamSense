#!/usr/bin/env python3
"""
IoT Anomaly Detection Model Trainer
Trains machine learning models for temperature and vibration anomaly detection.
"""

import pandas as pd
import numpy as np
import os
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import joblib
import logging
from google.cloud import bigquery
from datetime import datetime, timedelta
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnomalyDetectionTrainer:
    def __init__(self, project_id):
        self.project_id = project_id
        self.bq_client = bigquery.Client(project=project_id)
        self.dataset_id = "iot_data"
        self.table_id = "sensor_readings"
        self.model_dir = "./ml-models"
        
        # Create model directory if it doesn't exist
        os.makedirs(self.model_dir, exist_ok=True)
        
    def fetch_training_data(self, days_back=30):
        """Fetch training data from BigQuery"""
        try:
            # Calculate the date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Query for temperature and vibration data
            query = f"""
            SELECT 
                device_id,
                timestamp,
                temperature,
                vibration,
                is_anomaly
            FROM `{self.project_id}.{self.dataset_id}.{self.table_id}`
            WHERE timestamp >= '{start_date.isoformat()}'
            ORDER BY timestamp
            """
            
            # Execute query
            df = self.bq_client.query(query).to_dataframe()
            logger.info(f"Fetched {len(df)} records for training")
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching training data: {e}")
            return None
    
    def prepare_features(self, df):
        """Prepare features for anomaly detection"""
        try:
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Extract time-based features
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            
            # Calculate statistical features
            # Group by device to calculate moving averages and z-scores
            df_sorted = df.sort_values(['device_id', 'timestamp'])
            
            # Moving averages (5-point window)
            df_sorted['temp_ma'] = df_sorted.groupby('device_id')['temperature'].rolling(window=5, min_periods=1).mean().reset_index(0, drop=True)
            df_sorted['vibration_ma'] = df_sorted.groupby('device_id')['vibration'].rolling(window=5, min_periods=1).mean().reset_index(0, drop=True)
            
            # Z-scores
            df_sorted['temp_zscore'] = df_sorted.groupby('device_id', group_keys=False)['temperature'].apply(lambda x: (x - x.mean()) / x.std()).reset_index(0, drop=True)
            df_sorted['vibration_zscore'] = df_sorted.groupby('device_id', group_keys=False)['vibration'].apply(lambda x: (x - x.mean()) / x.std()).reset_index(0, drop=True)
            
            # Select features for training
            feature_columns = ['temperature', 'vibration', 'hour', 'day_of_week', 'temp_ma', 'vibration_ma', 'temp_zscore', 'vibration_zscore']
            X = df_sorted[feature_columns].fillna(0)
            
            return X, df_sorted
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return None, None
    
    def train_isolation_forest(self, X, y_true, model_name):
        """Train an Isolation Forest model with evaluation"""
        try:
            # Split data for evaluation
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_true, test_size=0.2, random_state=42, stratify=y_true
            )
            
            # Standardize features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train Isolation Forest
            model = IsolationForest(
                contamination=0.1,  # Expected proportion of anomalies
                random_state=42,
                n_estimators=100
            )
            model.fit(X_train_scaled)
            
            # Make predictions (-1 for anomaly, 1 for normal)
            y_pred = model.predict(X_test_scaled)
            # Convert to binary (1 for anomaly, 0 for normal)
            y_pred_binary = (y_pred == -1).astype(int)
            
            # Evaluate model
            self.evaluate_model(y_test, y_pred_binary, model_name)
            
            # Save model and scaler
            joblib.dump(model, f"{self.model_dir}/{model_name}_model.pkl")
            joblib.dump(scaler, f"{self.model_dir}/{model_name}_scaler.pkl")
            
            logger.info(f"Trained and saved {model_name} model")
            return model, scaler
            
        except Exception as e:
            logger.error(f"Error training Isolation Forest model: {e}")
            return None, None
    
    def evaluate_model(self, y_true, y_pred, model_name):
        """Evaluate model performance"""
        try:
            # Classification report
            report = classification_report(y_true, y_pred, target_names=['Normal', 'Anomaly'])
            logger.info(f"\n{model_name} Model Performance:\n{report}")
            
            # Confusion matrix
            cm = confusion_matrix(y_true, y_pred)
            logger.info(f"\n{model_name} Confusion Matrix:\n{cm}")
            
            # Calculate metrics
            tn, fp, fn, tp = cm.ravel()
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            logger.info(f"{model_name} Metrics - Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}")
            
            # Save evaluation metrics
            metrics = {
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'confusion_matrix': cm.tolist()
            }
            
            import json
            with open(f"{self.model_dir}/{model_name}_metrics.json", 'w') as f:
                json.dump(metrics, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
    
    def train_models(self):
        """Train all anomaly detection models"""
        try:
            # Fetch training data
            df = self.fetch_training_data()
            if df is None or df.empty:
                logger.warning("No training data available")
                return
            
            # Prepare features
            X, df_processed = self.prepare_features(df)
            if X is None:
                logger.error("Failed to prepare features")
                return
            
            # Train temperature anomaly detection model
            temp_features = ['temperature', 'hour', 'day_of_week', 'temp_ma', 'temp_zscore']
            X_temp = df_processed[temp_features].fillna(0)
            y_temp = df_processed['is_anomaly'].fillna(0)
            self.train_isolation_forest(X_temp, y_temp, "temperature")
            
            # Train vibration anomaly detection model
            vibration_features = ['vibration', 'hour', 'day_of_week', 'vibration_ma', 'vibration_zscore']
            X_vibration = df_processed[vibration_features].fillna(0)
            y_vibration = df_processed['is_anomaly'].fillna(0)
            self.train_isolation_forest(X_vibration, y_vibration, "vibration")
            
            logger.info("All models trained successfully")
            
        except Exception as e:
            logger.error(f"Error in training process: {e}")

def main():
    # Configuration - get from environment variables or use defaults
    PROJECT_ID = os.getenv("PROJECT_ID", "iotintel-streamsense")  # Use the correct project ID
    
    # Create trainer
    trainer = AnomalyDetectionTrainer(project_id=PROJECT_ID)
    
    # Train models
    trainer.train_models()

if __name__ == "__main__":
    main()
