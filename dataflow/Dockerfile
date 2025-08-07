FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the pipeline code
COPY pipeline.py .
COPY test_connection.py .
COPY test_pipeline.py .

# Command to run the pipeline
CMD ["python", "pipeline.py", "--project_id", "iotintel-streamsense", "--subscription_name", "iot-data-subscription", "--dataset_id", "iot_data", "--table_id", "sensor_readings"]
