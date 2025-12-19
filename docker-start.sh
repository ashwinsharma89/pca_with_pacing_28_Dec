#!/bin/bash
# Quick start script for PCA Agent Docker setup

echo "=========================================="
echo "PCA Agent - Docker Quick Start"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found"
    echo "Creating .env from .env.docker..."
    cp .env.docker .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys!"
    echo "   - OPENAI_API_KEY"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - JWT_SECRET_KEY"
    echo ""
    read -p "Press Enter to continue after editing .env..."
fi

echo "Building and starting services..."
docker-compose up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 10

echo ""
echo "=========================================="
echo "Services Status:"
echo "=========================================="
docker-compose ps

echo ""
echo "=========================================="
echo "Access Points:"
echo "=========================================="
echo "🌐 API:          http://localhost:8000"
echo "📚 API Docs:     http://localhost:8000/api/docs"
echo "🎨 Streamlit:    http://localhost:8501"
echo "📊 Prometheus:   http://localhost:9090"
echo "📈 Grafana:      http://localhost:3000 (admin/admin)"
echo ""

echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo "1. Initialize database:"
echo "   docker-compose exec api python scripts/init_database.py"
echo ""
echo "2. Create admin user:"
echo "   docker-compose exec api python scripts/init_users.py"
echo ""
echo "3. View logs:"
echo "   docker-compose logs -f"
echo ""
echo "4. Stop services:"
echo "   docker-compose down"
echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
