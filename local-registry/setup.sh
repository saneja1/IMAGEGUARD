#!/bin/bash

# ImageGuard Registry Setup Script
# This script sets up and starts the local Docker registry

set -e

echo "====================================="
echo "ImageGuard Local Registry Setup"
echo "====================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose is not installed"
    echo "Please install docker-compose first"
    exit 1
fi

echo "✅ Docker is installed"
echo "✅ docker-compose is installed"
echo ""

# Create data directory if it doesn't exist
mkdir -p data
echo "✅ Created data directory for persistent storage"
echo ""

# Start the registry
echo "Starting Docker registry..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 5

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ Registry is running!"
    echo ""
    echo "📊 Access points:"
    echo "   - Registry API: http://localhost:5000"
    echo "   - Web UI: http://localhost:8080"
    echo ""
    echo "🧪 Test the registry:"
    echo "   curl http://localhost:5000/v2/_catalog"
    echo ""
    echo "📖 See README.md for usage instructions"
else
    echo ""
    echo "❌ Error: Containers failed to start"
    echo "Check logs with: docker-compose logs"
    exit 1
fi
