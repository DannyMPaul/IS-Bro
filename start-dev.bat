@echo off
echo 🚀 Starting Idea Shaper Development Environment

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)

echo 📦 Installing backend dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install backend dependencies
    pause
    exit /b 1
)

echo 📦 Installing frontend dependencies...
cd ..\frontend
call npm install
if errorlevel 1 (
    echo ❌ Failed to install frontend dependencies
    pause
    exit /b 1
)

echo 🎯 Starting services...

echo 🔧 Starting FastAPI backend on port 8000...
cd ..\backend
start "Backend" python main.py

echo 🌐 Starting Next.js frontend on port 3000...
cd ..\frontend
start "Frontend" npm run dev

echo ✅ Services started!
echo 📱 Frontend: http://localhost:3000
echo 🔌 Backend API: http://localhost:8000  
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause >nul
