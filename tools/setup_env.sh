#!/bin/bash

# TODO: Update the script for windows, unix, macOS
# TODO: Add installation steps for redis, celery

sudo apt-get update
sudo apt-get install libsox-dev
sudo apt-get install sox -y
sudo apt install ffmpeg -y
python -m pip install --upgrade pip
python -m pip install *.whl
