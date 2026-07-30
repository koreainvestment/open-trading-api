#!/bin/bash

# Simple script to serve the frontend locally
# Usage: ./serve.sh [port]
# Note: Make sure to build first with 'npm run build'

PORT=${1:-3000}

# Check if dist directory exists
if [ ! -d "dist" ]; then
    echo "Error: dist directory not found. Please build first:"
    echo "  npm install"
    echo "  npm run build"
    exit 1
fi

echo "Starting web server on port $PORT..."
echo "Open http://localhost:$PORT in your browser"
echo "Press Ctrl+C to stop"
echo ""

# Try different methods to start a server
if command -v python3 &> /dev/null; then
    python3 -m http.server $PORT --directory dist
elif command -v python &> /dev/null; then
    # Python 2 SimpleHTTPServer doesn't support --directory easily, cd in subshell
    (cd dist && python -m SimpleHTTPServer $PORT)
elif command -v php &> /dev/null; then
    php -S localhost:$PORT -t dist
else
    echo "No suitable server found. Please install Python or PHP, or use a different HTTP server."
    exit 1
fi
