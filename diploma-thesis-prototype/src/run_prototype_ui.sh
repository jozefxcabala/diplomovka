#!/bin/bash

MODE="all"
RELOAD_FLAG="--reload"
EXPERIMENTS_MODE="false"

# Check for argument
if [ "$1" == "--backend" ]; then
    MODE="backend"
elif [ "$1" == "--frontend" ]; then
    MODE="frontend"
elif [ "$1" == "--prod" ]; then
    MODE="all"
    RELOAD_FLAG=""
elif [ "$1" == "--stop" ]; then
    MODE="stop"
elif [ "$1" == "--experiments" ]; then
    MODE="experiments"
    EXPERIMENTS_MODE="true"
fi

# 🛑 Stop mode
if [ "$MODE" == "stop" ]; then
    echo "🛑 Stopping all running servers..."
    pkill -f "python3 -m http.server"
    pkill -f "uvicorn"
    pkill -f "npm start"
    echo "✅ All processes terminated."
    exit 0
fi

# Activate virtual environment if it exists
if [ -d "backend/venv" ]; then
    source backend/venv/bin/activate
fi

# 📂 Start HTTP server for video hosting
if [ "$MODE" == "backend" ] || [ "$MODE" == "all" ]; then
    echo "📂 Starting HTTP server for video hosting..."
    cd ../data || exit
    python3 -m http.server 8001 > ../../http_server.log 2>&1 &
    cd ../src || exit
fi

# 🚀 Start FastAPI backend
if [ "$MODE" == "backend" ] || [ "$MODE" == "all" ] || [ "$MODE" == "experiments" ]; then
    echo "🚀 Starting FastAPI backend..."
    PYTHONPATH=src uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 $RELOAD_FLAG > backend.log 2>&1 &
fi

# 🌍 Start React frontend
if [ "$MODE" == "frontend" ] || [ "$MODE" == "all" ]; then
    echo "🌍 Starting standard React frontend..."
    cd frontend || exit
    npm start > ../frontend.log 2>&1 &
    cd ..
fi

# 🧪 Start experimental React frontend (on port 3001)
if [ "$EXPERIMENTS_MODE" == "true" ]; then
    echo "🧪 Starting experiments frontend on port 3001..."
    cd experiments-ui-frontend || exit
    PORT=3001 npm start > ../experiments-ui-frontend.log 2>&1 &
    cd ..
fi

# 🪵 Show logs
if [ "$MODE" == "all" ]; then
    tail -f backend.log frontend.log
elif [ "$MODE" == "backend" ]; then
    tail -f backend.log
elif [ "$MODE" == "frontend" ]; then
    tail -f frontend.log
elif [ "$MODE" == "experiments" ]; then
    tail -f backend.log experiments-ui-frontend.log
fi