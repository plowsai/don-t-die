#!/usr/bin/env python3
"""
Gunicorn configuration file for Don't Die application
"""
import multiprocessing

# Basic settings
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120

# Security settings
limit_request_line = 4096
limit_request_fields = 100

# Server mechanics
daemon = False
pidfile = None

# Logging
errorlog = "-"
loglevel = "info"
accesslog = "-"
access_log_format = '%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Monitoring
statsd_host = None 