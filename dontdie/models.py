from datetime import datetime
from flask import current_app
from flask_login import UserMixin
from dontdie import db, login_manager

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Association table for user friendships
friendships = db.Table('friendships',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Bio and personal information
    first_name = db.Column(db.String(30), nullable=True)
    last_name = db.Column(db.String(30), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    
    # Relationships
    tributes_sent = db.relationship('Tribute', 
                                    foreign_keys='Tribute.author_id',
                                    backref='author', 
                                    lazy='dynamic')
    
    tributes_received = db.relationship('Tribute', 
                                         foreign_keys='Tribute.recipient_id',
                                         backref='recipient', 
                                         lazy='dynamic')
    
    # Friends relationship (many-to-many self-referential)
    friends = db.relationship(
        'User', secondary=friendships,
        primaryjoin=(friendships.c.user_id == id),
        secondaryjoin=(friendships.c.friend_id == id),
        backref=db.backref('friended_by', lazy='dynamic'),
        lazy='dynamic'
    )
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
        
    def add_friend(self, user):
        if not self.is_friend(user):
            self.friends.append(user)
            return self
            
    def remove_friend(self, user):
        if self.is_friend(user):
            self.friends.remove(user)
            return self
            
    def is_friend(self, user):
        return self.friends.filter(friendships.c.friend_id == user.id).count() > 0


class Tribute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Visibility status (private until user chooses to make it visible to recipient)
    is_visible = db.Column(db.Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f"Tribute('{self.title}', '{self.created_at}')" 