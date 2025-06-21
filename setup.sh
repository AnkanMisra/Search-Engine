#!/bin/bash

# Search Engine MVP Setup Script
set -e

echo "🔍 Search Engine MVP Setup"
echo "========================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Meilisearch Configuration
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_KEY=masterKey123
INDEX_NAME=documents

# Backend Configuration
PORT=8080
GIN_MODE=release

# Crawler Configuration
MAX_PAGES=20
CRAWL_DELAY=2.0
REQUEST_TIMEOUT=15
USER_AGENT=SearchEngine-Crawler/1.0

# Custom seed URLs (comma-separated)
SEED_URLS=
EOF
    echo "✅ Created .env file"
fi

# Function to check if service is healthy
wait_for_service() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $service to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo "✅ $service is ready!"
            return 0
        fi
        echo "   Attempt $attempt/$max_attempts - waiting..."
        sleep 2
        ((attempt++))
    done
    
    echo "❌ $service failed to start after $max_attempts attempts"
    return 1
}

# Start the main services
echo "🚀 Starting services..."
docker-compose up -d meilisearch backend frontend

# Wait for services to be ready
wait_for_service "Meilisearch" "http://localhost:7700/health"
wait_for_service "Backend API" "http://localhost:8080/health"
wait_for_service "Frontend" "http://localhost:3000/"

echo ""
echo "🎉 Services are running!"
echo ""
echo "📊 Service URLs:"
echo "   Frontend:     http://localhost:3000"
echo "   Backend API:  http://localhost:8080"
echo "   Meilisearch:  http://localhost:7700"
echo ""
echo "📝 Next steps:"
echo "   1. Run the crawler to index content:"
echo "      docker-compose run --rm crawler"
echo ""
echo "   2. Or use the profile to run crawler:"
echo "      docker-compose --profile crawler up crawler"
echo ""
echo "   3. Visit http://localhost:3000 to start searching!"
echo ""
echo "🛠️  Useful commands:"
echo "   - View logs: docker-compose logs -f [service]"
echo "   - Stop all: docker-compose down"
echo "   - Rebuild: docker-compose up --build"
echo ""
echo "✨ Happy searching!" 