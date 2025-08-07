FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the trainer code
COPY trainer.py .

# Command to run the trainer
CMD ["python", "trainer.py"]
