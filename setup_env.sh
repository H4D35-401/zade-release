#!/bin/bash

# ZADE IGNITE - Setup Script
# Automates the creation of a virtual environment and installs dependencies.

echo "Initializing ZADE IGNITE Setup..."

# Check for python3
if ! command -v python3 &> /dev/null
then
    echo "Error: python3 could not be found. Please install it first."
    exit 1
fi

# Create venv
echo "Creating virtual environment..."
python3 -m venv venv

# Activate venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r src/requirements.txt

echo "Setup complete. Use ./run_zade.sh to launch the application."
