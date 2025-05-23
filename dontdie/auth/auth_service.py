"""
Authentication service for Supabase integration
"""
from flask import current_app, session, request, redirect, url_for
from .supabase_client import get_supabase_client
from supabase.client import Client as SupabaseClient
from jose import jwt
import json

class AuthService:
    """Service for handling authentication with Supabase"""
    
    @staticmethod
    def sign_up(email, password, metadata=None):
        """
        Register a new user with Supabase auth
        
        Args:
            email: User's email
            password: User's password
            metadata: Optional user metadata dict
            
        Returns:
            User data on success, error message on failure
        """
        try:
            supabase = get_supabase_client()
            user_data = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": metadata or {}
                }
            })
            return user_data
        except Exception as e:
            current_app.logger.error(f"Supabase signup error: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def sign_in(email, password):
        """
        Sign in a user with Supabase auth
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            Session data on success, error message on failure
        """
        try:
            supabase = get_supabase_client()
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            # Store access token and refresh token in session
            session['access_token'] = response.session.access_token
            session['refresh_token'] = response.session.refresh_token
            return response
        except Exception as e:
            current_app.logger.error(f"Supabase signin error: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def sign_out():
        """
        Sign out the current user
        """
        try:
            supabase = get_supabase_client()
            response = supabase.auth.sign_out()
            # Clear session
            session.pop('access_token', None)
            session.pop('refresh_token', None)
            return response
        except Exception as e:
            current_app.logger.error(f"Supabase signout error: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def reset_password(email):
        """
        Send a password reset email
        
        Args:
            email: User's email
            
        Returns:
            Success or error message
        """
        try:
            supabase = get_supabase_client()
            response = supabase.auth.reset_password_email(email)
            return {"success": True, "message": "Password reset email sent"}
        except Exception as e:
            current_app.logger.error(f"Supabase password reset error: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def get_user():
        """
        Get the current authenticated user
        
        Returns:
            User data or None
        """
        if 'access_token' not in session:
            return None
            
        try:
            supabase = get_supabase_client()
            # Get user from token
            user = supabase.auth.get_user(session['access_token'])
            return user
        except Exception as e:
            current_app.logger.error(f"Supabase get user error: {str(e)}")
            session.pop('access_token', None)
            session.pop('refresh_token', None)
            return None
    
    @staticmethod
    def require_auth(f):
        """
        Decorator for routes that require authentication
        """
        def decorated(*args, **kwargs):
            if 'access_token' not in session:
                return redirect(url_for('users.login'))
            
            try:
                supabase = get_supabase_client()
                # Verify token is valid
                user = supabase.auth.get_user(session['access_token'])
                if not user:
                    return redirect(url_for('users.login'))
            except:
                return redirect(url_for('users.login'))
                
            return f(*args, **kwargs)
        return decorated 