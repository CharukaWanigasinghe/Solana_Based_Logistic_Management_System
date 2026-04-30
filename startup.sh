#!/bin/bash

# Azure App Service startup script for INTELLICA Logistics System

echo "Starting INTELLICA Logistics System deployment..."

# Install system dependencies
apt-get update
apt-get install -y libpq-dev gcc curl

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements-azure.txt

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Create necessary directories
mkdir -p /tmp/uploads
mkdir -p /tmp/logs

# Set environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)

echo "Application startup complete. Starting server..."

# Start the application with Gunicorn
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:$PORT \
  --log-level info \
  --access-logfile - \
  --error-logfile -</content>
<parameter name="filePath">c:\Users\acer\Documents\SLIIT UNI\Research Related\PP1\Solana Based Logistic Management System\startup.sh