#!/bin/bash

# Install Python venv
sudo apt update
sudo apt install -y python3-venv

# Create and activate virtual environment
python3 -m venv gemai
source gemai/bin/activate

# Install required Python packages
pip install --upgrade google-cloud-aiplatform
pip install -r requirements.txt

# Authenticate with Google Cloud Platform
gcloud init
gcloud auth application-default login

# Activate gemai venv
source gemai/bin/activate