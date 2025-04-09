#!/bin/bash

MODE="all"
RELOAD_FLAG="--reload"

# Check for argument
if [ "$1" == "--backend" ]; then
    MODE="backend"
elif [ "$1" == "--frontend" ]; then
    MODE="frontend"
elif [ "$1" == "--prod" ]; then
    MODE="all"
    RELOAD_FLAG=""  # no reload in production
elif [ "$1" == "--stop" ]; then
    MODE="stop"
fi

# 🛑 Stop mode: kill running processes
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
if [ "$MODE" == "backend" ] || [ "$MODE" == "all" ]; then
    echo "🚀 Starting FastAPI backend..."
    PYTHONPATH=src uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 $RELOAD_FLAG > backend.log 2>&1 &
fi

# 🌍 Start React frontend
if [ "$MODE" == "frontend" ] || [ "$MODE" == "all" ]; then
    echo "🌍 Starting React frontend..."
    cd frontend || exit

    if [ "$1" == "--prod" ]; then
        npm start > ../frontend.log 2> ../eslint.log &
    else
        npm start > ../frontend.log 2>&1 &
    fi

    cd ..
fi

# 🪵 Show logs
if [ "$MODE" == "all" ]; then
    tail -f backend.log frontend.log
elif [ "$MODE" == "backend" ]; then
    tail -f backend.log
elif [ "$MODE" == "frontend" ]; then
    tail -f frontend.log
fi
