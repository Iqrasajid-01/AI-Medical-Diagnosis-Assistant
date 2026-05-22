"""
SQLAlchemy database models for the Medical AI application.
"""
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """User account model."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')  # 'admin' or 'user'
    created_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    predictions = db.relationship(
        'PredictionHistory', backref='user', lazy=True,
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        """Serialize user to dictionary (excludes password)."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
        }

    def __repr__(self):
        return f'<User {self.username}>'


class PredictionHistory(db.Model):
    """Stores each prediction made by a user."""
    __tablename__ = 'prediction_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False
    )
    disease_type = db.Column(db.String(50), nullable=False)  # diabetes, heart, parkinsons
    input_data = db.Column(db.JSON, nullable=False)
    prediction_result = db.Column(db.Integer, nullable=False)  # 0 or 1
    confidence = db.Column(db.Float, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        """Serialize prediction to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'disease_type': self.disease_type,
            'input_data': self.input_data,
            'prediction_result': self.prediction_result,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat(),
        }

    def __repr__(self):
        return f'<Prediction {self.disease_type} user={self.user_id}>'
