#!/bin/bash
# Production deployment script for running Don't Die with Gunicorn

# Exit on errors
set -e

# Configuration variables - customize these
APP_NAME="dontdie"
NUM_WORKERS=4                  # Recommended: 2 * number of CPUs + 1
PORT=${PORT:-8000}             # Use PORT env var or default to 8000
LOG_DIR="/var/log/dontdie"     # Log directory
ACCESS_LOG="$LOG_DIR/access.log"
ERROR_LOG="$LOG_DIR/error.log"
APP_DIR=$(dirname $(readlink -f "$0"))
TIMEOUT=60
APP_USER=${APP_USER:-$(whoami)}

# Create log directory if it doesn't exist
mkdir -p $LOG_DIR
chmod 755 $LOG_DIR

# Print deployment information
echo "===== Don't Die Application Deployment ====="
echo "Deploying as user: $APP_USER"
echo "App directory: $APP_DIR"
echo "Workers: $NUM_WORKERS"
echo "Port: $PORT"
echo "Timeout: $TIMEOUT seconds"
echo "Logs: $LOG_DIR"
echo "==========================================="

# Set up Python path
cd $APP_DIR
export PYTHONPATH=$APP_DIR:$PYTHONPATH

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "Loading environment variables from .env file..."
    set -a
    source .env
    set +a
fi

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "Error: Gunicorn not found. Please install it with 'pip install gunicorn'"
    exit 1
fi

# Start Gunicorn
echo "Starting Gunicorn server for Don't Die application..."
exec gunicorn wsgi:app \
    --name $APP_NAME \
    --bind 0.0.0.0:$PORT \
    --workers $NUM_WORKERS \
    --timeout $TIMEOUT \
    --log-level info \
    --access-logfile $ACCESS_LOG \
    --error-logfile $ERROR_LOG \
    --capture-output \
    --preload \
    --forwarded-allow-ips="*" \
    "$@" 