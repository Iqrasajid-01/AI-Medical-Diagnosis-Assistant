"""
Authentication routes — register, login, and profile.
"""
import datetime
import functools

import jwt
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash

from backend.models.db_models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


# ── JWT helpers ──────────────────────────────────────────────────────────────

def create_token(user):
    """Issue a JWT for *user*."""
    payload = {
        'user_id': user.id,
        'role': user.role,
        'exp': datetime.datetime.now(datetime.timezone.utc)
               + datetime.timedelta(hours=current_app.config['JWT_EXPIRATION_HOURS']),
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def decode_token(token):
    """Return the payload dict or *None* on failure."""
    try:
        return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def token_required(f):
    """Decorator – injects *current_user* into the wrapped view."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), 401

        payload = decode_token(auth_header.split(' ')[1])
        if payload is None:
            return jsonify({'error': 'Token expired or invalid'}), 401

        user = User.query.get(payload['user_id'])
        if user is None:
            return jsonify({'error': 'User not found'}), 401

        return f(current_user=user, *args, **kwargs)
    return wrapper


def admin_required(f):
    """Decorator – same as *token_required* but also enforces role='admin'."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), 401

        payload = decode_token(auth_header.split(' ')[1])
        if payload is None:
            return jsonify({'error': 'Token expired or invalid'}), 401

        user = User.query.get(payload['user_id'])
        if user is None:
            return jsonify({'error': 'User not found'}), 401
        if user.role != 'admin':
            return jsonify({'error': 'Admin privileges required'}), 403

        return f(current_user=user, *args, **kwargs)
    return wrapper


# ── Routes ───────────────────────────────────────────────────────────────────

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}

    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not username or not email or not password:
        return jsonify({'error': 'Username, email, and password are required'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    if User.query.filter((User.email == email) | (User.username == username)).first():
        return jsonify({'error': 'Username or email already exists'}), 409

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role='user',
    )
    db.session.add(user)
    db.session.commit()

    token = create_token(user)
    return jsonify({'token': token, 'user': user.to_dict()}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if user is None or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = create_token(user)
    return jsonify({'token': token, 'user': user.to_dict()}), 200


@auth_bp.route('/profile', methods=['GET'])
@token_required
def profile(current_user):
    return jsonify({'user': current_user.to_dict()}), 200
