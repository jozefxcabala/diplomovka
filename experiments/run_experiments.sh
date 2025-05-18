#!/bin/bash

# This script automates the execution of multiple experiments using payloads defined in a JSON file.
#
# Functionality:
# - Verifies existence of required dataset and downloads it if missing.
# - Starts the FastAPI backend server in the background using Conda.
# - Reads a list of experiment configurations (payloads) from a given JSON file.
# - Sends each payload to the backend for execution and saves the results as JSON.
# - Measures and logs execution time per experiment.
# - Cleans up by terminating the backend after all experiments are finished.
#
# Usage:
#   ./run_experiments.sh <payload_file.json>

# === SETTINGS ===
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$ROOT_DIR/src"
DATASET_DIR="$ROOT_DIR/experiments/UBnormal"
ZIP_PATH="$ROOT_DIR/experiments/UBnormal.zip"
MODEL_PATH="data/models/yolo11n.pt"
BACKEND_LOG="$ROOT_DIR/logs/experiment_backend.log"
RESULTS_DIR="$ROOT_DIR/experiments/results"
NEXTCLOUD_URL="https://nextcloud.fit.vutbr.cz/s/k6JtN8objCS2SHa/download"

# === Check payload file name (relative to experiments/) ===
if [ -z "$1" ]; then
  echo "❌ Please provide the payload file name located in experiments/ folder."
  echo "Usage: ./run_experiments.sh experiment_payloads.json"
  exit 1
fi

PAYLOADS_FILE="$ROOT_DIR/experiments/$1"

if [ ! -f "$PAYLOADS_FILE" ]; then
  echo "❌ File not found: $PAYLOADS_FILE"
  exit 1
fi

mkdir -p "$ROOT_DIR/logs"
mkdir -p "$RESULTS_DIR"

 # Gracefully handle termination signals (e.g., Ctrl+C)
# === Trap termination ===
trap "echo '🛑 Caught termination signal. Killing backend...'; kill $BACKEND_PID; exit 1" SIGINT SIGTERM

# === 1. Download Dataset ===
echo "📦 Checking UBnormal dataset..."
if [ ! -d "$DATASET_DIR" ]; then
    echo "⬇️  UBnormal dataset not found. Downloading from Nextcloud..."
    curl -L "$NEXTCLOUD_URL" -o "$ZIP_PATH"
    if [ -f "$ZIP_PATH" ]; then
        echo "📦 Unzipping dataset..."
        unzip "$ZIP_PATH" -d "$ROOT_DIR/experiments"
        rm "$ZIP_PATH"
        echo "✅ Dataset ready."
    else
        echo "❌ Failed to download dataset."
        exit 1
    fi
else
    echo "✅ UBnormal dataset already exists."
fi

# === 2. Start Backend ===
echo "🚀 Starting FastAPI backend..."
cd "$SRC_DIR" || exit 1
conda run --no-capture-output -n diploma-thesis-prototype \
  uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --workers 1 \
  > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

# === 3. Wait for Backend ===
echo "⏳ Waiting for backend to start..."
until curl -s http://127.0.0.1:8000/docs > /dev/null; do
  sleep 1
done
echo "✅ Backend is up."

# === 4. Iterate over payloads from file ===
echo "🔁 Reading payloads from $PAYLOADS_FILE..."
INDEX=0
PAYLOADS=()
while IFS= read -r line; do
  PAYLOADS+=("$line")
done < <(jq -c '.[]' "$PAYLOADS_FILE")

for PAYLOAD in "${PAYLOADS[@]}"; do
  START_EPOCH=$(date +%s)
  START_HUMAN=$(date "+%Y-%m-%d %H:%M:%S")

  echo "🔬 Running experiment #$INDEX..."
  echo "🕒 Started at: $START_HUMAN"

  RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/experiments/ubnormal/run \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

  OUT_FILE="$RESULTS_DIR/experiment_result_${INDEX}_$(date +%Y%m%d_%H%M%S).json"
  echo "{ \"request_data\": $PAYLOAD, \"result_data\": $RESPONSE }" > "$OUT_FILE"

  END_EPOCH=$(date +%s)
  END_HUMAN=$(date "+%Y-%m-%d %H:%M:%S")
  DURATION=$((END_EPOCH - START_EPOCH))

  HOURS=$(printf "%02d" $((DURATION / 3600)))
  MINUTES=$(printf "%02d" $(((DURATION % 3600) / 60)))
  SECONDS=$(printf "%02d" $((DURATION % 60)))

  echo "✅ Saved result to $OUT_FILE"
  echo "🏁 Finished at: $END_HUMAN (duration: ${DURATION} seconds (=${HOURS}:${MINUTES}:${SECONDS}))"
  echo "----------------------------------------"

  INDEX=$((INDEX+1))
done

# === 5. Cleanup ===
echo "🛑 Stopping backend (PID $BACKEND_PID)"
kill $BACKEND_PID
echo "🏁 All experiments completed."