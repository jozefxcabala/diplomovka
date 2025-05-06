#!/bin/bash

MODE="all"
RELOAD_FLAG="--reload"
EXPERIMENTS_MODE="false"

# Absolute path to logs directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/../logs"

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

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Activate virtual environment if it exists
if [ -d "backend/venv" ]; then
    source backend/venv/bin/activate
fi

# 📂 Start HTTP server for video hosting
if [ "$MODE" == "backend" ] || [ "$MODE" == "all" ]; then
    echo "📂 Starting HTTP server for video hosting..."
    cd ../data || exit
    python3 -m http.server 8001 > "$LOG_DIR/http_server.log" 2>&1 &
    cd ../src || exit
fi

# 🧪 Download UBnormal dataset if running experiments
if [ "$EXPERIMENTS_MODE" == "true" ]; then
    cd "$SCRIPT_DIR" || exit
    DATASET_DIR="../experiments/UBnormal"
    FILE_ID="1KbfdyasribAMbbKoBU1iywAhtoAt9QI0"
    ZIP_PATH="../experiments/UBnormal.zip"

    if [ ! -d "$DATASET_DIR" ]; then
        echo "⬇️  UBnormal dataset not found. Downloading..."
        
        # Check for gdown
        if ! command -v gdown &> /dev/null; then
            echo "⚠️  gdown not found. Installing..."
            pip install gdown
        fi

        gdown "$FILE_ID" -O "$ZIP_PATH"

        if [ -f "$ZIP_PATH" ]; then
            echo "📦 Unzipping dataset..."
            unzip "$ZIP_PATH" -d "../experiments/"
            rm "$ZIP_PATH"
            echo "✅ UBnormal dataset ready."
        else
            echo "❌ Failed to download UBnormal dataset."
        fi
    else
        echo "✅ UBnormal dataset already present."
    fi
fi

# 🚀 Start FastAPI backend
if [ "$MODE" == "backend" ] || [ "$MODE" == "all" ] || [ "$MODE" == "experiments" ]; then
    echo "🚀 Starting FastAPI backend..."
    PYTHONPATH=src uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 $RELOAD_FLAG > "$LOG_DIR/backend.log" 2>&1 &
fi

# 🌍 Start React frontend
if [ "$MODE" == "frontend" ] || [ "$MODE" == "all" ]; then
    echo "🌍 Starting standard React frontend..."
    cd frontend || exit
    npm start > "$LOG_DIR/frontend.log" 2>&1 &
    cd ..
fi

# 🧪 Start experimental React frontend (on port 3001)
if [ "$EXPERIMENTS_MODE" == "true" ]; then
    echo "🧪 Starting experiments frontend on port 3001..."
    cd experiments-ui-frontend || exit
    PORT=3001 npm start > "$LOG_DIR/experiments-ui-frontend.log" 2>&1 &
    cd ..
fi

# 🪵 Show logs
if [ "$MODE" == "all" ]; then
    tail -f "$LOG_DIR/backend.log" "$LOG_DIR/frontend.log"
elif [ "$MODE" == "backend" ]; then
    tail -f "$LOG_DIR/backend.log"
elif [ "$MODE" == "frontend" ]; then
    tail -f "$LOG_DIR/frontend.log"
elif [ "$MODE" == "experiments" ]; then
    tail -f "$LOG_DIR/backend.log" "$LOG_DIR/experiments-ui-frontend.log"
fi