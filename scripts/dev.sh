#!/bin/bash

# ============================================================
# 🚀 Hotel Booking System - Development Setup
# ============================================================

set -e

echo "🏨 Hotel Booking System - Development Setup"
echo "============================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Database Configuration
POSTGRES_USER=hotel_user
POSTGRES_PASSWORD=hotel_password
POSTGRES_DB=hotel_booking
DATABASE_URL=postgresql://hotel_user:hotel_password@postgres:5432/hotel_booking

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Application Configuration
PROJECT_NAME=Hotel Booking System
SECRET_KEY=your-super-secret-key-change-in-production-$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin User
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_PASSWORD=admin123

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Email Configuration (Update with your settings)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_FROM_NAME=Hotel Booking System
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_STARTTLS=true
MAIL_SSL_TLS=false

# Frontend URL
FRONTEND_URL=http://localhost:3000
EOF
    echo "✅ .env file created with default values"
    echo "⚠️  Please update email settings in .env file"
fi

# Build and start services
echo "🔨 Building containers..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🏥 Checking service health..."

# Check backend
if curl -f http://localhost:8000/docs > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is not responding"
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend is not responding"
fi

echo ""
echo "🎉 Development environment is ready!"
echo ""
echo "📋 Available Services:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo "   Database:  localhost:5433"
echo "   Redis:     localhost:6379"
echo ""
echo "👤 Default Admin Credentials:"
echo "   Email:     admin@example.com"
echo "   Password:  admin123"
echo ""
echo "🔧 Useful Commands:"
echo "   make logs     - View logs"
echo "   make down     - Stop services"
echo "   make clean    - Clean up"
echo "   make shell    - Access backend shell"
echo ""
