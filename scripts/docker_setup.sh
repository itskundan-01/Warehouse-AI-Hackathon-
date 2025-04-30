#!/bin/bash

# Script to set up and validate Docker environment for WarehouseVision AI
echo "Setting up Docker environment for WarehouseVision AI..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit https://docs.docker.com/get-docker/ for installation instructions."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check Docker version
docker_version=$(docker --version)
echo "✅ Docker is installed: $docker_version"

# Check if Docker Compose is installed (V1 or V2)
if command -v docker-compose &> /dev/null; then
    compose_version=$(docker-compose --version)
    echo "✅ Docker Compose V1 is installed: $compose_version"
elif docker compose version &> /dev/null; then
    compose_version=$(docker compose version)
    echo "✅ Docker Compose V2 is installed: $compose_version"
else
    echo "❌ Docker Compose is not installed. Please install Docker Compose and try again."
    echo "Visit https://docs.docker.com/compose/install/ for installation instructions."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it to configure your environment."
else
    echo "✅ .env file already exists."
fi

# Create necessary directories
mkdir -p data/images data/videos models/yolo models/ocr models/facial logs

# Pull required Docker images
echo "Pulling required Docker images..."
docker pull postgres:14-alpine
docker pull redis:6-alpine
docker pull rabbitmq:3-management-alpine
docker pull docker.elastic.co/elasticsearch/elasticsearch:7.14.0
docker pull docker.elastic.co/kibana/kibana:7.14.0
docker pull docker.elastic.co/logstash/logstash:7.14.0

# Build project Docker images
echo "Building project Docker images..."
docker-compose build || docker compose build

echo ""
echo "Docker environment setup complete!"
echo ""
echo "Now you can run the following commands to start the services:"
echo "1. docker-compose up -d   # Start all services in detached mode"
echo "2. docker-compose logs -f  # Follow the logs of all services"
echo ""
echo "For development, you may want to run specific services only:"
echo "- docker-compose up -d db redis rabbitmq  # Start only dependencies"
echo "- python src/main.py  # Run the API server locally for development"
