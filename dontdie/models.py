from datetime import datetime
from flask import current_app
from flask_login import UserMixin
from dontdie import db, login_manager

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper table for friend relationships
friends = db.Table(
    'friends',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    tributes_received = db.relationship('Tribute', 
                                    foreign_keys='Tribute.recipient_id',
                                    backref='recipient', 
                                    lazy='dynamic')
    
    tributes_given = db.relationship('Tribute', 
                                    foreign_keys='Tribute.author_id',
                                    backref='author', 
                                    lazy='dynamic')
    
    # Friend relationship (self-referential)
    followed = db.relationship(
        'User', secondary=friends,
        primaryjoin=(friends.c.follower_id == id),
        secondaryjoin=(friends.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    
    def add_friend(self, user):
        if not self.is_friend(user):
            self.followed.append(user)
            user.followed.append(self)
    
    def remove_friend(self, user):
        if self.is_friend(user):
            self.followed.remove(user)
            user.followed.remove(self)
    
    def is_friend(self, user):
        return self.followed.filter(friends.c.followed_id == user.id).count() > 0
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Tribute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    is_visible = db.Column(db.Boolean, default=False, nullable=False)
    
    # Foreign keys
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"Tribute('{self.title}', '{self.created_at}')" 