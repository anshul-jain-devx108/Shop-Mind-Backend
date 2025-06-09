from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from ..models import User
from .. import db
from ..utils import hash_password, verify_password
import uuid

auth_bp = Blueprint('auth', __name__)

def create_tokens(user_id, session_id):
    expires = timedelta(hours=1)
    access_token = create_access_token(identity=user_id, expires_delta=expires, additional_claims={'session_id': session_id})
    refresh_token = create_refresh_token(identity=user_id, additional_claims={'session_id': session_id})
    return access_token, refresh_token, expires.total_seconds()

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not all([name, email, password]):
        return jsonify({'error': 'Missing fields'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(
        id=str(uuid.uuid4()),
        name=name,
        email=email,
        password_hash=hash_password(password),
        is_guest=False
    )
    db.session.add(user)
    db.session.commit()

    # Create new chat session for user
    session_id = str(uuid.uuid4())

    access_token, refresh_token, expires_in = create_tokens(user.id, session_id)

    return jsonify({
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email
        },
        'token': access_token,
        'refreshToken': refresh_token,
        'sessionId': session_id,
        'expiresIn': expires_in,
        'loginTime': datetime.utcnow().isoformat() + 'Z'
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({'error': 'Missing fields'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(user.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    session_id = str(uuid.uuid4())

    access_token, refresh_token, expires_in = create_tokens(user.id, session_id)

    return jsonify({
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email
        },
        'token': access_token,
        'refreshToken': refresh_token,
        'sessionId': session_id,
        'expiresIn': expires_in,
        'loginTime': datetime.utcnow().isoformat() + 'Z'
    })

@auth_bp.route('/guest', methods=['POST'])
def guest_login():
    # Create a guest user on the fly
    guest_user = User(
        id=str(uuid.uuid4()),
        name='Guest',
        email=None,
        password_hash=None,
        is_guest=True
    )
    db.session.add(guest_user)
    db.session.commit()

    session_id = str(uuid.uuid4())
    access_token, refresh_token, expires_in = create_tokens(guest_user.id, session_id)

    return jsonify({
        'user': {
            'id': guest_user.id,
            'name': guest_user.name,
            'email': None
        },
        'token': access_token,
        'refreshToken': refresh_token,
        'sessionId': session_id,
        'expiresIn': expires_in,
        'loginTime': datetime.utcnow().isoformat() + 'Z'
    })

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'is_guest': user.is_guest,
        'created_at': user.created_at.isoformat() + 'Z'
    })
