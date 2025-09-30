#!/bin/bash

# Create and activate Python virtual environment
echo "Creating Python virtual environment..."
python -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r backend/requirements.txt

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm ci

# Build frontend
echo "Building frontend..."
npm run build

# Start backend (which will serve both API and frontend)
echo "Starting backend with frontend..."
cd backend
source ../venv/bin/activate
python -m uvicorn api_endpoints:app --host 0.0.0.0 --port $PORT

