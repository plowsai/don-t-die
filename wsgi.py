#!/usr/bin/env python3
"""
WSGI entry point for Don't Die application
"""
from dontdie import create_app

app = create_app()

if __name__ == '__main__':
    app.run() 