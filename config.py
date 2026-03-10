"""
Configuration settings for ScholarFix
"""

import os
from datetime import timedelta

class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'scholarfix-dev-secret-key-2024')
    
    # Database
    DATABASE_PATH = 'database/users.db'
    
    # Upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'docx', 'pdf', 'txt'}
    
    # Session settings
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Processing settings
    MAX_DAILY_DOCUMENTS = {
        'free': 5,
        'student': 10,
        'professional': 20,
        'premium': 100
    }
    
    # API settings
    API_RATE_LIMIT = '100/day'
    
    # Paths
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    @staticmethod
    def init_app(app):
        """Initialize app with config"""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = False
    TESTING = True
    DATABASE_PATH = ':memory:'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        # Production-specific initialization
        pass

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}