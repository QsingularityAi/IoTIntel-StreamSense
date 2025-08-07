FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server code
COPY server.py .

# Expose port
EXPOSE 8000

# Command to run the server
CMD ["python", "server.py"]
