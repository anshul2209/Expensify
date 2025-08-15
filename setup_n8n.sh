#!/bin/bash

# n8n Setup Script for Expense Management System
# This script helps you set up n8n for the expense automation workflow

echo "🚀 Setting up n8n for Expense Management System..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create n8n data directory
echo "📁 Creating n8n data directory..."
mkdir -p ~/n8n-data

# Generate encryption key
echo "🔐 Generating encryption key..."
ENCRYPTION_KEY=$(openssl rand -hex 16)
echo "Generated encryption key: $ENCRYPTION_KEY"

# Create docker-compose.yml
echo "📝 Creating docker-compose.yml..."
cat > docker-compose.yml << EOF
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=expense123
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://localhost:5678/
      - N8N_ENCRYPTION_KEY=$ENCRYPTION_KEY
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=n8n_password
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    container_name: n8n-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=n8n
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=n8n_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  n8n_data:
  postgres_data:
EOF

echo "✅ Created docker-compose.yml"

# Start n8n
echo "🚀 Starting n8n..."
docker-compose up -d

# Wait for n8n to start
echo "⏳ Waiting for n8n to start..."
sleep 30

# Check if n8n is running
if curl -s http://localhost:5678 > /dev/null; then
    echo "✅ n8n is running successfully!"
    echo ""
    echo "🌐 Access n8n at: http://localhost:5678"
    echo "👤 Username: admin"
    echo "🔑 Password: expense123"
    echo ""
    echo "📋 Next steps:"
    echo "1. Open http://localhost:5678 in your browser"
    echo "2. Login with admin/expense123"
    echo "3. Import the workflow: n8n-workflows/expense-automation.json"
    echo "4. Configure your credentials (Gmail, OpenRouter, Supabase)"
    echo "5. Activate the workflow"
    echo ""
    echo "📚 For detailed setup instructions, see: docs/setup.md"
else
    echo "❌ n8n failed to start. Check the logs:"
    echo "docker-compose logs n8n"
fi
