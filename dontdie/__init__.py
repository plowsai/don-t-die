import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-development-only')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///dontdie.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Import and register blueprints
    from dontdie.main.routes import main
    from dontdie.users.routes import users
    from dontdie.tributes.routes import tributes
    from dontdie.errors.handlers import errors
    
    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(tributes)
    app.register_blueprint(errors)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    return app 