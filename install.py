#!/usr/bin/env python3
"""
ScholarFix Installation Script
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def print_header():
    """Print installation header"""
    print("=" * 60)
    print("SCHOLARFIX INSTALLATION")
    print("=" * 60)

def check_python_version():
    """Check Python version"""
    print("\n1. Checking Python version...")
    if sys.version_info < (3, 7):
        print("ERROR: Python 3.7 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected")

def create_directories():
    """Create necessary directories"""
    print("\n2. Creating directories...")
    
    directories = [
        'processing',
        'templates',
        'static',
        'database',
        'utils',
        'uploads/original',
        'uploads/processed',
        'uploads/previews',
        'tests'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  Created: {directory}/")
    
    print("✓ All directories created")

def install_dependencies():
    """Install Python dependencies"""
    print("\n3. Installing dependencies...")
    
    requirements = [
        'Flask==2.3.3',
        'Flask-Session==0.5.0',
        'Werkzeug==2.3.7',
        'python-docx==0.8.11',
        'PyPDF2==3.0.1',
        'spacy==3.6.1',
        'language-tool-python==2.7.1',
        'nltk==3.8.1',
        'reportlab==4.0.4',
        'python-multipart==0.0.6'
    ]
    
    try:
        for package in requirements:
            print(f"  Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
        print("✓ All dependencies installed")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        sys.exit(1)

def download_nlp_models():
    """Download NLP models"""
    print("\n4. Downloading NLP models...")
    
    try:
        print("  Downloading spaCy model...")
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        
        print("  Downloading NLTK data...")
        import nltk
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('averaged_perceptron_tagger')
        
        print("✓ NLP models downloaded")
        
    except Exception as e:
        print(f"✗ Failed to download NLP models: {e}")
        print("  Note: Some features may not work correctly")

def setup_database():
    """Setup database"""
    print("\n5. Setting up database...")
    
    try:
        # Read schema
        with open('database/schema.sql', 'r') as f:
            schema = f.read()
        
        # Create database
        conn = sqlite3.connect('database/users.db')
        cursor = conn.cursor()
        
        # Execute schema
        cursor.executescript(schema)
        conn.commit()
        conn.close()
        
        print("✓ Database created and initialized")
        
    except Exception as e:
        print(f"✗ Failed to setup database: {e}")
        sys.exit(1)

def create_config_file():
    """Create configuration file"""
    print("\n6. Creating configuration file...")
    
    config_content = '''"""
ScholarFix Configuration
"""

import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'scholarfix-dev-secret-key-change-in-production')
    DATABASE_PATH = 'database/users.db'
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'docx', 'pdf', 'txt'}
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    @staticmethod
    def init_app(app):
        pass

config = Config()
'''
    
    with open('config.py', 'w') as f:
        f.write(config_content)
    
    print("✓ Configuration file created")

def create_requirements_file():
    """Create requirements.txt file"""
    print("\n7. Creating requirements.txt...")
    
    requirements = '''Flask==2.3.3
Flask-Session==0.5.0
Werkzeug==2.3.7
python-docx==0.8.11
PyPDF2==3.0.1
spacy==3.6.1
language-tool-python==2.7.1
nltk==3.8.1
reportlab==4.0.4
python-multipart==0.0.6
'''
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    
    print("✓ requirements.txt created")

def create_test_user():
    """Create test user"""
    print("\n8. Creating test user...")
    
    try:
        import sqlite3
        from werkzeug.security import generate_password_hash
        
        conn = sqlite3.connect('database/users.db')
        cursor = conn.cursor()
        
        # Check if test user exists
        cursor.execute("SELECT id FROM users WHERE email = 'test@scholarfix.com'")
        if cursor.fetchone():
            print("  Test user already exists")
        else:
            # Create test user
            cursor.execute('''
                INSERT INTO users (email, name, password_hash, user_type, max_documents)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                'test@scholarfix.com',
                'Test User',
                generate_password_hash('test123'),
                'professional',
                50
            ))
            conn.commit()
            print("✓ Test user created: test@scholarfix.com / test123")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Failed to create test user: {e}")

def print_final_instructions():
    """Print final instructions"""
    print("\n" + "=" * 60)
    print("INSTALLATION COMPLETE!")
    print("=" * 60)
    print("\nTo start ScholarFix:")
    print("1. cd scholarfix")
    print("2. python app.py")
    print("3. Open http://localhost:5000 in your browser")
    print("\nTest credentials:")
    print("  Email: test@scholarfix.com")
    print("  Password: test123")
    print("\nDefault user limits:")
    print("  Free: 5 documents/day")
    print("  Student: 10 documents/day")
    print("  Professional: 20 documents/day")
    print("  Premium: 100 documents/day")
    print("\nFor production deployment:")
    print("1. Set SECRET_KEY environment variable")
    print("2. Use a production WSGI server (Gunicorn)")
    print("3. Use a production database (PostgreSQL)")
    print("=" * 60)

def main():
    """Main installation function"""
    print_header()
    
    steps = [
        check_python_version,
        create_directories,
        install_dependencies,
        download_nlp_models,
        create_config_file,
        create_requirements_file,
        setup_database,
        create_test_user,
        print_final_instructions
    ]
    
    for step in steps:
        try:
            step()
        except KeyboardInterrupt:
            print("\n\nInstallation cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"\nERROR: Step failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()