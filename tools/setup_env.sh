#!/bin/bash

# TODO: Update the script for Windows, Unix, macOS
# Depending on the platform, you may need to adjust package installation commands and paths.

# TODO: Add installation steps for Redis and Celery
# Provide instructions for installing Redis and Celery here.

# NOTE: It is suggested to run this script in python virtual env

# Check if the system is running on macOS (Darwin)
if [[ "$(uname)" == "Darwin" ]]; then
    # macOS-specific commands (you may need to install these packages via Homebrew)
    brew update
    brew install sox
    brew install ffmpeg
    brew install redis
    brew services start redis
else
    # Assuming Unix-based systems (Linux)
    sudo apt-get update
    sudo apt-get install libsox-dev
    sudo apt-get install sox -y
    sudo apt install ffmpeg -y

    # Install Redis
    sudo apt-get install redis-server -y
    # Start Redis server on boot
    sudo systemctl enable redis-server
    # Start Redis server now
    sudo systemctl start redis-server
fi

# Python package installation
python -m pip install --upgrade pip
pip install -r requirements.txt
python setup.py install
