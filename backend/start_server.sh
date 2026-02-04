#!/bin/bash

echo "========================================"
echo "ExamyNex Backend Quick Start"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "#" ]; then
    echo "Creating virtual environment..."
    python3 -m venv #
fi

# Activate virtual environment
echo "Activating virtual environment..."
source #/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirments.txt

# Start the server
echo ""
echo "========================================"
echo "Starting FastAPI server..."
echo "Backend will be available at:"
echo "http://localhost:8000"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
