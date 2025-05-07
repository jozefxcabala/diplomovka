#!/bin/bash
set -e

ENV_NAME="diploma-thesis-prototype"
DB_DIR="$HOME/pg-diploma-thesis-prototype-data"

echo "✅ Creating conda environment..."
conda env create -f ./enviroments/diploma-thesis-prototype-env-linux.yml

echo "✅ Activating environment and setting up PostgreSQL..."
# Run further commands inside the activated environment
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate $ENV_NAME

# Initialize the database if it doesn't already exist
if [ ! -d "$DB_DIR" ]; then
  echo "✅ Initializing database in $DB_DIR..."
  initdb -D "$DB_DIR" -U postgres
fi

# Start the database
echo "🚀 Starting PostgreSQL server..."
pg_ctl -D "$DB_DIR" -l "$DB_DIR/logfile.log" start

echo "✅ Done. PostgreSQL is running and the environment is ready."