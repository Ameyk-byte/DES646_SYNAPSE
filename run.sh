#!/bin/bash

echo "=========================================="
echo "  Starting Neuro AI Assistant"
echo "=========================================="

if [ ! -d "venv" ]; then
  echo "🔧 Creating virtual environment..."
  python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt >/dev/null

python3 main.py

