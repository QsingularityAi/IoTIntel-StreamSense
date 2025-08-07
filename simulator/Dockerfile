FROM python:3.9-slim

WORKDIR /app

# Set environment variable for Google credentials
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/credentials.json"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the simulator code and credentials
COPY iot_simulator.py .
COPY credentials.json .

# Command to run the simulator
CMD ["python", "iot_simulator.py"]
