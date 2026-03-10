#!/usr/bin/env python3
"""
ScholarFix Setup Script
"""

import os
import sys
import subprocess

def install_requirements():
    """Install Python requirements"""
    print("Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def download_spacy_model():
    """Download spaCy model"""
    print("Downloading spaCy model...")
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])

def download_nltk_data():
    """Download NLTK data"""
    print("Downloading NLTK data...")
    import nltk
    nltk.download('punkt')
    nltk.download('stopwords')

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    directories = [
        'uploads/original',
        'uploads/processed', 
        'uploads/previews',
        'processing',
        'database',
        'utils',
        'templates',
        'static',
        'tests'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("Directories created successfully!")

def setup_database():
    """Initialize database"""
    print("Setting up database...")
    from database.db_handler import DatabaseHandler
    db = DatabaseHandler('database/users.db')
    db.init_db()
    print("Database initialized successfully!")

def main():
    """Main setup function"""
    print("=" * 50)
    print("ScholarFix Setup")
    print("=" * 50)
    
    try:
        create_directories()
        install_requirements()
        download_spacy_model()
        download_nltk_data()
        setup_database()
        
        print("\n" + "=" * 50)
        print("Setup completed successfully!")
        print("\nTo run ScholarFix:")
        print("1. cd scholarfix")
        print("2. python app.py")
        print("3. Open http://localhost:5000 in your browser")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nSetup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()