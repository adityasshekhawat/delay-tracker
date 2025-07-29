FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY processor.py .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command
ENTRYPOINT ["python", "processor.py"] 