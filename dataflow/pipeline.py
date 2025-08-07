#!/usr/bin/env python3
"""
IoT Dataflow Pipeline
Real-time processing pipeline for IoT sensor data using Apache Beam and Dataflow.
"""

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import StandardOptions
from apache_beam.options.pipeline_options import GoogleCloudOptions
from apache_beam.options.pipeline_options import WorkerOptions
import json
import argparse
from datetime import datetime
import requests

class ParseMessage(beam.DoFn):
    """Parse Pub/Sub messages into Python dictionaries"""
    def process(self, element):
        try:
            # Parse the message
            message = json.loads(element)
            
            # Add processing timestamp
            message['processed_at'] = datetime.now().isoformat()
            
            yield message
        except Exception as e:
            # Log and skip malformed messages
            print(f"Error parsing message: {e}")
            yield beam.pvalue.TaggedOutput('errors', element)

class AddAnomalyScores(beam.DoFn):
    """Add anomaly scores to messages using ML models"""
    def process(self, element):
        try:
            # In a real implementation, this would call the ML server
            # For now, we'll just add placeholder scores
            element['temp_anomaly_score'] = 0.0
            element['vibration_anomaly_score'] = 0.0
            
            # If it's already marked as an anomaly, keep that status
            if element.get('is_anomaly', False):
                element['temp_anomaly_score'] = -0.5
                element['vibration_anomaly_score'] = -0.5
            
            yield element
        except Exception as e:
            print(f"Error adding anomaly scores: {e}")
            yield beam.pvalue.TaggedOutput('errors', element)

class PreprocessData(beam.DoFn):
    """Preprocess sensor data to add statistical features"""
    def process(self, element):
        try:
            # In a production system, this would calculate moving averages and z-scores
            # based on historical data. For now, we'll add placeholder values.
            element['sensor_data']['temp_ma'] = element['sensor_data']['temperature']  # Moving average
            element['sensor_data']['vibration_ma'] = element['sensor_data']['vibration']  # Moving average
            element['sensor_data']['temp_zscore'] = 0.0  # Z-score
            element['sensor_data']['vibration_zscore'] = 0.0  # Z-score
            
            yield element
        except Exception as e:
            print(f"Error preprocessing data: {e}")
            yield beam.pvalue.TaggedOutput('errors', element)

class DetectAnomaliesWithML(beam.DoFn):
    """Detect anomalies using the ML server"""
    def process(self, element):
        try:
            # Prepare data for ML server
            ml_data = {
                'device_id': element['device_id'],
                'timestamp': element['timestamp'],
                'temperature': element['sensor_data']['temperature'],
                'vibration': element['sensor_data']['vibration']
            }
            
            # Call ML server for anomaly detection
            # In a local development environment, this would be http://ml-server:8000
            # In production, this would be the actual ML serving endpoint
            ml_server_url = "http://ml-server:8000/detect"
            
            try:
                response = requests.post(ml_server_url, json=ml_data, timeout=5)
                if response.status_code == 200:
                    result = response.json()
                    # Update element with ML results
                    element['is_anomaly'] = result.get('is_anomaly', False)
                    element['sensor_data']['temp_anomaly_score'] = result.get('temp_anomaly_score', 0.0)
                    element['sensor_data']['vibration_anomaly_score'] = result.get('vibration_anomaly_score', 0.0)
                else:
                    print(f"ML server returned status code {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Error calling ML server: {e}")
                # Keep existing values if ML server is unavailable
                pass
            
            yield element
        except Exception as e:
            print(f"Error detecting anomalies with ML: {e}")
            yield beam.pvalue.TaggedOutput('errors', element)

class SendAlerts(beam.DoFn):
    """Send alerts for detected anomalies"""
    def process(self, element):
        try:
            # Only send alerts for anomalies
            if element.get('is_anomaly', False):
                # Prepare alert data
                alert_data = {
                    'device_id': element['device_id'],
                    'timestamp': element['timestamp'],
                    'alert_type': 'anomaly_detected',
                    'severity': 'high',
                    'message': f"Anomaly detected for device {element['device_id']}",
                    'temperature': element['sensor_data']['temperature'],
                    'vibration': element['sensor_data']['vibration']
                }
                
                # Add anomaly type if present
                if 'anomaly_type' in element['sensor_data']:
                    alert_data['anomaly_type'] = element['sensor_data']['anomaly_type']
                
                # Call alert endpoint
                # In a production system, this might send emails, SMS, or integrate with alerting systems
                ml_server_url = "http://ml-server:8000/alert"
                
                try:
                    response = requests.post(ml_server_url, json=alert_data, timeout=5)
                    if response.status_code != 200:
                        print(f"Alert server returned status code {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"Error sending alert: {e}")
            
            yield element
        except Exception as e:
            print(f"Error sending alerts: {e}")
            yield beam.pvalue.TaggedOutput('errors', element)

class FormatForBigQuery(beam.DoFn):
    """Format messages for BigQuery insertion"""
    def process(self, element):
        try:
            # Flatten the structure for BigQuery
            bq_row = {
                'device_id': element['device_id'],
                'timestamp': element['timestamp'],
                'processed_at': element['processed_at'],
                'building': element['location']['building'],
                'floor': element['location']['floor'],
                'room': element['location']['room'],
                'device_type': element['device_type'],
                'temperature': element['sensor_data']['temperature'],
                'vibration': element['sensor_data']['vibration'],
                'is_anomaly': element['is_anomaly'],
                'temp_anomaly_score': element['sensor_data'].get('temp_anomaly_score', 0.0),
                'vibration_anomaly_score': element['sensor_data'].get('vibration_anomaly_score', 0.0)
            }
            
            # Add anomaly type if present
            if 'anomaly_type' in element['sensor_data']:
                bq_row['anomaly_type'] = element['sensor_data']['anomaly_type']
            
            # Add statistical features
            bq_row['temp_ma'] = element['sensor_data'].get('temp_ma', 0.0)
            bq_row['vibration_ma'] = element['sensor_data'].get('vibration_ma', 0.0)
            bq_row['temp_zscore'] = element['sensor_data'].get('temp_zscore', 0.0)
            bq_row['vibration_zscore'] = element['sensor_data'].get('vibration_zscore', 0.0)
            
            yield bq_row
        except Exception as e:
            print(f"Error formatting for BigQuery: {e}")
            yield beam.pvalue.TaggedOutput('errors', element)

def run_pipeline(project_id, subscription_name, dataset_id, table_id):
    """Run the Dataflow pipeline"""
    
    # Set up pipeline options
    options = PipelineOptions()
    google_cloud_options = options.view_as(GoogleCloudOptions)
    google_cloud_options.project = project_id
    google_cloud_options.job_name = f'iot-anomaly-detection-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
    google_cloud_options.region = 'us-central1'
    
    # For local development, use DirectRunner without staging locations
    runner = options.view_as(StandardOptions).runner
    if not runner or runner == 'DirectRunner':
        print(f"Running locally with DirectRunner for project: {project_id}")
        # Don't set staging/temp locations for local runs
        options.view_as(StandardOptions).streaming = True
    else:
        # For cloud runs, set up staging locations
        google_cloud_options.staging_location = f'gs://{project_id}-dataflow/staging'
        google_cloud_options.temp_location = f'gs://{project_id}-dataflow/temp'
        options.view_as(StandardOptions).streaming = True
        
        # Set up worker options for cloud runs
        options.view_as(WorkerOptions).max_num_workers = 5
        options.view_as(WorkerOptions).autoscaling_algorithm = 'THROUGHPUT_BASED'
    
    # Create the pipeline
    print(f"Creating pipeline with project_id: {project_id}")
    print(f"Subscription: projects/{project_id}/subscriptions/{subscription_name}")
    
    try:
        with beam.Pipeline(options=options) as pipeline:
            # Read from Pub/Sub
            messages = (
                pipeline
            | 'Read from Pub/Sub' >> beam.io.ReadFromPubSub(
                subscription=f'projects/{project_id}/subscriptions/{subscription_name}'
            )
            | 'Parse Messages' >> beam.ParDo(ParseMessage()).with_outputs('errors', main='parsed')
        )
        
        # Preprocess data to add statistical features
        preprocessed_messages = (
            messages.parsed
            | 'Preprocess Data' >> beam.ParDo(PreprocessData()).with_outputs('errors', main='preprocessed')
        )
        
        # Detect anomalies using ML server
        ml_detected_messages = (
            preprocessed_messages.preprocessed
            | 'Detect Anomalies with ML' >> beam.ParDo(DetectAnomaliesWithML()).with_outputs('errors', main='detected')
        )
        
        # Send alerts for detected anomalies
        alert_messages = (
            ml_detected_messages.detected
            | 'Send Alerts' >> beam.ParDo(SendAlerts()).with_outputs('errors', main='alerted')
        )
        
        # Format for BigQuery and write
        bq_rows = (
            alert_messages.alerted
            | 'Format for BigQuery' >> beam.ParDo(FormatForBigQuery())
            | 'Write to BigQuery' >> beam.io.WriteToBigQuery(
                table=f'{project_id}:{dataset_id}.{table_id}',
                schema='device_id:STRING,timestamp:TIMESTAMP,processed_at:TIMESTAMP,building:STRING,floor:INTEGER,room:STRING,device_type:STRING,temperature:FLOAT,vibration:FLOAT,is_anomaly:BOOLEAN,temp_anomaly_score:FLOAT,vibration_anomaly_score:FLOAT,anomaly_type:STRING,temp_ma:FLOAT,vibration_ma:FLOAT,temp_zscore:FLOAT,vibration_zscore:FLOAT',
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
            )
        )
        
        # Handle errors from all new steps
        preprocessing_errors = preprocessed_messages.errors
        ml_errors = ml_detected_messages.errors
        alert_errors = alert_messages.errors
        
        errors = (
            (messages.errors, preprocessing_errors, ml_errors, alert_errors)
            | 'Flatten All Errors' >> beam.Flatten()
            | 'Print Errors' >> beam.Map(print)
        )
        
    except Exception as e:
        print(f"❌ Pipeline execution failed: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='IoT Anomaly Detection Dataflow Pipeline')
    parser.add_argument('--project_id', required=True, help='GCP project ID')
    parser.add_argument('--subscription_name', required=True, help='Pub/Sub subscription name')
    parser.add_argument('--dataset_id', required=True, help='BigQuery dataset ID')
    parser.add_argument('--table_id', required=True, help='BigQuery table ID')
    
    args = parser.parse_args()
    
    run_pipeline(
        project_id=args.project_id,
        subscription_name=args.subscription_name,
        dataset_id=args.dataset_id,
        table_id=args.table_id
    )
