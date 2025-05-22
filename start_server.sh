#!/bin/bash
# Script to start Gunicorn server for Don't Die application

# Set environment variables if needed
# export SECRET_KEY=your_secret_key
# export DATABASE_URL=your_database_url

# Activate virtual environment if needed
# source /path/to/venv/bin/activate

echo "Starting Gunicorn server for Don't Die application..."
gunicorn -c gunicorn_config.py wsgi:app 