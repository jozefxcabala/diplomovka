#!/bin/bash

# Aktivácia virtuálneho prostredia pre backend (ak používaš venv)
source backend/venv/bin/activate  # macOS/Linux
# source backend/venv/Scripts/activate  # Windows (ak používaš Git Bash)

echo "🚀 Spúšťam FastAPI backend..."
cd backend
uvicorn main:app --host 127.0.0.1 --port 8000 --reload 2>&1 | tee ../backend.log & 
cd ..

echo "🌍 Spúšťam React frontend..."
cd frontend
npm start 2>&1 | tee ../frontend.log & 
cd ..

# Udržiava terminál aktívny a zobrazuje oba logy súčasne
tail -f backend.log frontend.log
