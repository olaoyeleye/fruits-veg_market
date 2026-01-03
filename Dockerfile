# Use a slim Python image instead of full Ubuntu for a smaller pipeline footprint
FROM python:3.9-slim

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

# Install system dependencies (gcc etc. only if your python packages need them)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
# Create a requirements.txt if you don't have one
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy psycopg2-binary psycopg  
# Copy the rest of your code
COPY . /workspace

# The correct way to write the CMD
# Change "main:app" to "backend-api.main:app"
CMD ["uvicorn", "backend-api.main:app", "--host", "0.0.0.0", "--port", "8000"]
