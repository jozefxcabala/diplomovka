#!/bin/bash

# This script controls the startup, stop, and mode selection for the diploma thesis prototype system.
#
# Functionality:
# - Supports launching backend, frontend, or both (default).
# - Provides a mode for running experiments, including dataset download if needed.
# - Starts the HTTP server for video access and logs its output.
# - Activates a virtual environment for backend services if present.
# - Routes logs to the appropriate directory and supports graceful shutdown.
#
# Usage:
#   ./run_prototype_ui.sh [--backend | --frontend | --prod | --stop | --experiments]

MODE="all"
RELOAD_FLAG="--reload"
EXPERIMENTS_MODE="false"

# Absolute path to logs directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/../logs"
NEXTCLOUD_URL="https://nextcloud.fit.vutbr.cz/s/k6JtN8objCS2SHa/download"
DATASET_DIR="$SCRIPT_DIR/../experiments/UBnormal"
ZIP_PATH="$SCRIPT_DIR/../experiments/UBnormal.zip"

# Parse arguments
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

# Gracefully stop all running services if --stop is passed
if [ "$MODE" == "stop" ]; then
    echo "🛑 Stopping all running servers..."
    pkill -f "python3 -m http.server"
    pkill -f "uvicorn"
    pkill -f "npm start"
    echo "✅ All processes terminated."
    exit 0
fi

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
    echo "📦 Checking UBnormal dataset..."
    if [ ! -d "$DATASET_DIR" ]; then
        echo "⬇️  UBnormal dataset not found. Downloading from Nextcloud..."
        curl -L "$NEXTCLOUD_URL" -o "$ZIP_PATH"
        if [ -f "$ZIP_PATH" ]; then
            echo "📦 Unzipping dataset..."
            unzip "$ZIP_PATH" -d "$SCRIPT_DIR/../experiments"
            rm "$ZIP_PATH"
            echo "✅ UBnormal dataset ready."
        else
            echo "❌ Failed to download dataset from Nextcloud."
            exit 1
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