#!/bin/bash
# P1 Strategy Builder - Start Script
# Frontend: 3000, Backend: 8000

# Get absolute path of script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== P1 Strategy Builder ==="
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo ""

# Kill existing processes on these ports
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Start backend
cd "$SCRIPT_DIR"
echo "[Backend] Starting on port 8000..."
uv run python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend
sleep 2

# Ensure frontend deps are installed
if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
  echo "[Frontend] node_modules not found, running npm install..."
  (cd "$SCRIPT_DIR/frontend" && npm install) || { echo "npm install failed. Run: cd frontend && npm install"; exit 1; }
fi

# Start frontend
cd "$SCRIPT_DIR/frontend"
echo "[Frontend] Starting on port 3000..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Press Ctrl+C to stop all services"

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

wait
