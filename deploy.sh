#!/bin/bash
# Deploy TinkerTrack to production

set -e

echo "🚀 TinkerTrack Deployment Script"

# Check if .env.prod exists
if [ ! -f .env.prod ]; then
    echo "❌ .env.prod not found. Copy .env.example to .env.prod and update values."
    exit 1
fi

# Pull latest image
echo "📥 Pulling latest image from Docker Hub..."
docker pull veersc2007/tinkertrack:latest

# Stop old containers
echo "🛑 Stopping existing containers..."
docker compose -f docker-compose.prod.yml --env-file .env.prod down || true

# Start new containers
echo "▶️ Starting services..."
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Wait for database
echo "⏳ Waiting for database to be ready..."
sleep 10

# Check status
echo "✅ Deployment complete!"
echo ""
docker compose -f docker-compose.prod.yml ps
echo ""
echo "📊 API available at: http://localhost:8000/docs"
