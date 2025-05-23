import os
import secrets
from PIL import Image
from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app, session
from flask_login import login_user, current_user, logout_user, login_required
from dontdie import db, bcrypt, mail
from dontdie.models import User, Tribute
from dontdie.users.forms import RegistrationForm, LoginForm, UpdateProfileForm, RequestResetForm, ResetPasswordForm
from flask_mail import Message
from dontdie.auth.auth_service import AuthService
from functools import wraps

users = Blueprint('users', __name__)

# Custom login_required decorator using Supabase authentication
def supabase_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated with Supabase
        if 'access_token' not in session:
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('users.login'))
        
        # Get the current user from Supabase
        user_data = AuthService.get_user()
        if not user_data:
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('users.login'))
            
        return f(*args, **kwargs)
    return decorated_function

@users.route('/register', methods=['GET', 'POST'])
def register():
    if 'access_token' in session:
        return redirect(url_for('main.home'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        # Register with Supabase
        metadata = {
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'username': form.username.data
        }
        
        result = AuthService.sign_up(form.email.data, form.password.data, metadata)
        
        if 'error' in result:
            flash(f'Registration error: {result["error"]}', 'danger')
            return render_template('users/register.html', title='Register', form=form)
            
        # If auto-confirm is disabled in Supabase, show message about confirmation email
        flash('Your account has been created! Please check your email to confirm your registration before logging in.', 'success')
        return redirect(url_for('users.login'))
            
    return render_template('users/register.html', title='Register', form=form)

@users.route('/login', methods=['GET', 'POST'])
def login():
    if 'access_token' in session:
        return redirect(url_for('main.home'))
        
    form = LoginForm()
    if form.validate_on_submit():
        # Login with Supabase
        result = AuthService.sign_in(form.email.data, form.password.data)
        
        if 'error' in result:
            flash(f'Login unsuccessful. Please check email and password. {result.get("error")}', 'danger')
            return render_template('users/login.html', title='Login', form=form)
            
        # Get user data
        user_data = AuthService.get_user()
        
        if not user_data:
            flash('Error retrieving user data.', 'danger')
            return render_template('users/login.html', title='Login', form=form)
            
        # Sync with our database
        user = User.query.filter_by(email=form.email.data).first()
        
        if not user:
            # Create user in our database
            user = User.create_from_supabase(user_data.user)
        elif not user.supabase_uid:
            # Update existing user with Supabase UID
            user.supabase_uid = user_data.user.id
            db.session.commit()
            
        # Login with Flask-Login as well for compatibility
        login_user(user, remember=form.remember.data)
        
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main.home'))
            
    return render_template('users/login.html', title='Login', form=form)

@users.route('/logout')
def logout():
    # Sign out of Supabase
    if 'access_token' in session:
        AuthService.sign_out()
    
    # Sign out of Flask-Login
    logout_user()
    
    return redirect(url_for('main.home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    
    # Resize image
    output_size = (150, 150)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

@users.route('/profile', methods=['GET', 'POST'])
@supabase_login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('users.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.bio.data = current_user.bio
    
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('users/profile.html', title='Profile',
                           image_file=image_file, form=form)

@users.route('/user/<string:username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    image_file = url_for('static', filename='profile_pics/' + user.image_file)
    
    # If current user is viewing their own profile, show all tributes they've received that are visible
    visible_tributes = None
    if current_user.is_authenticated and current_user.id == user.id:
        visible_tributes = Tribute.query.filter_by(recipient_id=user.id, is_visible=True).all()
    
    return render_template('users/user_profile.html', title=user.username, user=user, 
                           image_file=image_file, visible_tributes=visible_tributes)

@users.route('/friends')
@login_required
def friends():
    # Get all friends
    user_friends = current_user.friends.all()
    return render_template('users/friends.html', title='My Friends', friends=user_friends)

@users.route('/users')
@login_required
def all_users():
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('users/all_users.html', title='Find Friends', users=users)

@users.route('/add_friend/<int:user_id>', methods=['POST'])
@login_required
def add_friend(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('You cannot add yourself as a friend.', 'danger')
        return redirect(url_for('users.all_users'))
    
    current_user.add_friend(user)
    db.session.commit()
    flash(f'You are now friends with {user.username}!', 'success')
    return redirect(url_for('users.all_users'))

@users.route('/remove_friend/<int:user_id>', methods=['POST'])
@login_required
def remove_friend(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('You cannot remove yourself as a friend.', 'danger')
        return redirect(url_for('users.friends'))
    
    current_user.remove_friend(user)
    db.session.commit()
    flash(f'You are no longer friends with {user.username}.', 'info')
    return redirect(url_for('users.friends'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if 'access_token' in session:
        return redirect(url_for('main.home'))
        
    form = RequestResetForm()
    if form.validate_on_submit():
        # Use Supabase password reset
        result = AuthService.reset_password(form.email.data)
        
        if 'error' in result:
            flash(f'Error: {result["error"]}', 'danger')
        else:
            flash('An email has been sent with instructions to reset your password.', 'info')
            
        return redirect(url_for('users.login'))
    return render_template('users/reset_request.html', title='Reset Password', form=form)

@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    # This is handled by Supabase directly, we just redirect
    flash('Please follow the reset link in your email to reset your password.', 'info')
    return redirect(url_for('users.login')) 