#!/bin/bash

# Check if Python 3.10 is installed
echo "Checking for Python 3.10..."
if ! python3.10 --version &>/dev/null; then
    echo "Python 3.10 is not installed. Please install Python 3.10 to proceed."
    exit 1
fi

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y libreoffice wkhtmltopdf

# Create a Python virtual environment
echo "Creating Python virtual environment..."
python3.10 -m venv venv

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip to the latest version
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "All dependencies installed successfully!"