import os
import secrets
from PIL import Image
from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from dontdie import db, bcrypt
from dontdie.models import User, Tribute
from dontdie.users.forms import RegistrationForm, LoginForm, UpdateProfileForm

users = Blueprint('users', __name__)

@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('users/register.html', title='Register', form=form)

@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('users/login.html', title='Login', form=form)

@users.route('/logout')
def logout():
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
@login_required
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