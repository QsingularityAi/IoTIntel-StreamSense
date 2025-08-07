FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the consumer code
COPY consumer.py .

# Command to run the consumer
CMD ["python", "consumer.py"]
