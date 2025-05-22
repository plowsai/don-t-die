from flask import Blueprint, render_template, request
from flask_login import current_user
from dontdie.models import User, Tribute
from datetime import datetime

main = Blueprint('main', __name__)

@main.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@main.route('/')
@main.route('/home')
def home():
    # Show different content based on auth status
    if current_user.is_authenticated:
        # For logged in users, show a personalized dashboard
        visible_tributes = Tribute.query.filter_by(
            recipient_id=current_user.id, 
            is_visible=True
        ).order_by(Tribute.created_at.desc()).limit(5).all()
        
        friends = current_user.friends.limit(5).all()
        
        return render_template('main/dashboard.html', 
                              tributes=visible_tributes,
                              friends=friends)
    else:
        # For anonymous users, show the landing page
        return render_template('main/landing.html')

@main.route('/landing')
def landing():
    return render_template('main/landing.html', title='Welcome')

@main.route('/about')
def about():
    return render_template('main/about.html', title='About')

@main.route('/tributes')
def tributes():
    tributes = Tribute.query.filter_by(is_visible=True).order_by(Tribute.created_at.desc()).all()
    return render_template('main/tributes.html', title='Tributes', tributes=tributes)

@main.route('/resources')
def resources():
    return render_template('main/resources.html', title='Resources')

@main.route('/faq')
def faq():
    return render_template('main/faq.html', title='FAQ') 