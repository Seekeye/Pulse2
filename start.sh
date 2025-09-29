#!/bin/bash

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r backend/requirements.txt

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm ci

# Build frontend
echo "Building frontend..."
npm run build

# Start both services
echo "Starting services..."
npm run start:all

