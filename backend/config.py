"""
Application configuration loaded from environment variables.
"""
import os
from dotenv import load_dotenv

# Load .env file from the backend directory
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BACKEND_DIR, '.env'))


class Config:
    """Flask application configuration."""

    # Flask core
    SECRET_KEY = os.getenv('SECRET_KEY', 'medical-ai-secret-key-2024')

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 'sqlite:///medical_ai.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))

    # File uploads
    UPLOAD_FOLDER = os.path.join(
        BACKEND_DIR, os.getenv('UPLOAD_FOLDER', 'uploads')
    )
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB

    # ML assets
    ML_ASSETS_DIR = os.path.join(
        BACKEND_DIR, os.getenv('ML_ASSETS_DIR', 'static/ml_assets')
    )

    # Datasets
    DATASETS_DIR = os.path.join(BACKEND_DIR, '..', 'datasets')

    # CORS
    CORS_ORIGINS = ['http://localhost:5173', 'http://127.0.0.1:5173']
