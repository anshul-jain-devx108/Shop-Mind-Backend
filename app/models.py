from datetime import datetime
import uuid
from . import db

def generate_uuid():
    return str(uuid.uuid4())

class User(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)  # nullable for guests
    password_hash = db.Column(db.String(255), nullable=True)
    is_guest = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    chat_sessions = db.relationship('ChatSession', backref='user', lazy=True)

class ChatSession(db.Model):
    session_id = db.Column(db.String, primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String, db.ForeignKey('user.id'))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    message_count = db.Column(db.Integer, default=0)

    messages = db.relationship('Message', backref='session', lazy=True)

class Message(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    session_id = db.Column(db.String, db.ForeignKey('chat_session.session_id'))
    content = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(10))  # 'user' or 'bot'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    products = db.Column(db.JSON, nullable=True)  # list of product ids

class Product(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50))
    price = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Float, default=0)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
