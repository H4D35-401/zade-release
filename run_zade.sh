#!/bin/bash

# ZADE IGNITE - Run Script
# Launches the application using the virtual environment.

if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run ./setup_env.sh first."
    exit 1
fi

source venv/bin/activate
python3 src/config_gui.py
