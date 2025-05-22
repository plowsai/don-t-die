#!/bin/bash
# Script to stop Gunicorn server for Don't Die application

echo "Stopping Gunicorn server for Don't Die application..."
pkill -f "gunicorn"

# Check if successful
if [ $? -eq 0 ]; then
    echo "Gunicorn server stopped successfully."
else
    echo "No Gunicorn processes found or unable to stop them."
fi 