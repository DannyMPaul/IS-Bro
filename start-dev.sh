#!/bin/bash

echo "🚀 Starting Idea Shaper Development Environment"

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt

echo "📦 Installing frontend dependencies..."
cd ../frontend
npm install

echo "🎯 Starting services..."

# Start backend in background
cd ../backend
echo "🔧 Starting FastAPI backend on port 8000..."
python main.py &
BACKEND_PID=$!

# Start frontend
cd ../frontend
echo "🌐 Starting Next.js frontend on port 3000..."
npm run dev &
FRONTEND_PID=$!

echo "✅ Services started!"
echo "📱 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"

# Wait for user to stop
echo "Press Ctrl+C to stop all services..."
wait

# Cleanup
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
echo "🛑 Services stopped"
