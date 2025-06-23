#!/bin/bash
set -e

echo "=== Build Script for HackerNews AI Chatbot ==="
echo "Python version:"
python --version

echo "Pip version:"
python -m pip --version

echo "Upgrading pip, setuptools, and wheel..."
python -m pip install --upgrade pip setuptools wheel

echo "Installing requirements..."
python -m pip install --no-cache-dir -r requirements.txt

echo "Build completed successfully!" 