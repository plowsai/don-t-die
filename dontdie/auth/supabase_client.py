"""
Supabase client configuration for authentication
"""
import os
from supabase import create_client
from flask import current_app

# Initialize Supabase client
def get_supabase_client():
    """
    Returns a configured Supabase client using environment variables
    """
    url = current_app.config.get('SUPABASE_URL')
    key = current_app.config.get('SUPABASE_KEY')
    
    if not url or not key:
        raise ValueError(
            "Supabase URL and API key must be set in environment variables "
            "SUPABASE_URL and SUPABASE_KEY or in app config"
        )
    
    return create_client(url, key) 