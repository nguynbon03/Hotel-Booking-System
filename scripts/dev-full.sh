#!/bin/bash

# Development script for Hotel Booking System
# This script starts both backend and frontend in development mode

set -e

echo "🚀 Starting Hotel Booking System in Development Mode..."

# Function to cleanup background processes
cleanup() {
    echo "🛑 Shutting down services..."
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}

# Trap cleanup function on script exit
trap cleanup EXIT INT TERM

# Start backend
echo "🔧 Starting Backend Server..."
cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install backend dependencies
echo "📦 Installing backend dependencies..."
pip install -r requirements.txt

# Start backend server
echo "🌐 Starting FastAPI server on http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🎨 Starting Frontend Server..."
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start frontend development server
echo "🌐 Starting React dev server on http://localhost:5173"
npm run dev &
FRONTEND_PID=$!

# Wait for both servers to start
sleep 2

echo "✅ Development servers started!"
echo "🔗 Frontend: http://localhost:5173"
echo "🔗 Backend API: http://localhost:8000"
echo "🔗 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for background processes
wait
