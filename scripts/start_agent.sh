#!/bin/bash
# OpenCLAW-2 Literary Agent — Linux Launch Script

echo "🦅 Starting OpenCLAW-2 Literary Agent..."

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
fi

# Launch
python main.py "$@"
