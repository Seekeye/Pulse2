#!/bin/bash

# Script de inicio para Railway
echo "🚀 Starting Pulse API..."

# Instalar dependencias si es necesario
pip install -r requirements.txt

# Iniciar la API
echo "📡 Starting API on port $PORT..."
python3 -m uvicorn api_endpoints:app --host 0.0.0.0 --port $PORT
