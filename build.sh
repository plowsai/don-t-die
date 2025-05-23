#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this file based on your specific setup needs
echo "Running build.sh"

# Python setup
python -m pip install --upgrade pip
pip install -r requirements.txt

# Create required directories if they don't exist
mkdir -p dontdie/static/profile_pics

# Create the database if it doesn't exist
python -c "from dontdie import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

echo "Build script completed" 