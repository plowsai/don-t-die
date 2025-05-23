from datetime import datetime, timedelta
from flask import current_app
from flask_login import UserMixin
from dontdie import db, login_manager
from itsdangerous import URLSafeTimedSerializer as Serializer

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
    supabase_uid = db.Column(db.String(36), unique=True, nullable=True)  # UUID from Supabase
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=True)  # Can be null for Supabase auth
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
    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt='password-reset-salt')
        
    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt='password-reset-salt', max_age=expires_sec)['user_id']
        except:
            return None
        return User.query.get(user_id)
    
    @classmethod
    def create_from_supabase(cls, user_data):
        """Create or update a user from Supabase auth data"""
        user = cls.query.filter_by(supabase_uid=user_data.id).first()
        
        if not user:
            # New user, create record
            user = cls(
                supabase_uid=user_data.id,
                email=user_data.email,
                username=user_data.email.split('@')[0],  # Default username from email
                first_name=user_data.user_metadata.get('first_name', ''),
                last_name=user_data.user_metadata.get('last_name', '')
            )
            db.session.add(user)
        else:
            # Update existing user
            user.email = user_data.email
            if user_data.user_metadata:
                if 'first_name' in user_data.user_metadata:
                    user.first_name = user_data.user_metadata['first_name']
                if 'last_name' in user_data.user_metadata:
                    user.last_name = user_data.user_metadata['last_name']
        
        db.session.commit()
        return user
    
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