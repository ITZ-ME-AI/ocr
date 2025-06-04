#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies
apt-get update
apt-get install -y tesseract-ocr
apt-get install -y libgl1-mesa-glx

# Verify Tesseract installation
if ! command -v tesseract &> /dev/null; then
    echo "Tesseract is not installed. Installing..."
    apt-get update
    apt-get install -y tesseract-ocr
fi

# Create symbolic link if it doesn't exist
if [ ! -f /usr/bin/tesseract ]; then
    echo "Creating symbolic link for tesseract..."
    ln -s $(which tesseract) /usr/bin/tesseract
fi

# Verify Tesseract path
echo "Verifying Tesseract installation..."
tesseract --version

# Install Python dependencies
pip install -r requirements.txt 