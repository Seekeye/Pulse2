#!/bin/bash

# Activate Python virtual environment (already created in install phase)
echo "Activating Python virtual environment..."
source venv/bin/activate

# Start backend API only
echo "Starting ChainPulse API Server..."
cd backend
source ../venv/bin/activate
python -m uvicorn api_endpoints:app --host 0.0.0.0 --port $PORT

