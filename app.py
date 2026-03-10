"""
ScholarFix - Main Flask Application
Document Refinement Tool with User Authentication
"""

import os
import uuid
import json
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Import custom modules
from processing.document_processor import DocumentProcessor
from processing.grammar import GrammarProcessor
from processing.tone import ToneAdjuster
from processing.formatting import FormattingProcessor
from utils.auth import login_required, generate_token, verify_token
from utils.file_handler import FileHandler
from database.db_handler import DatabaseHandler

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'scholarfix-secret-key-2024'),
    SESSION_TYPE='filesystem',
    SESSION_PERMANENT=False,
    SESSION_USE_SIGNER=True,
    UPLOAD_FOLDER='uploads',
    MAX_CONTENT_LENGTH=10 * 1024 * 1024,  # 10MB max file size
    ALLOWED_EXTENSIONS={'docx', 'pdf', 'txt'},
    DATABASE='database/users.db'
)

# Initialize extensions
Session(app)

# Initialize custom components
db_handler = DatabaseHandler(app.config['DATABASE'])
file_handler = FileHandler(app.config['UPLOAD_FOLDER'])
grammar_processor = GrammarProcessor()
tone_adjuster = ToneAdjuster()
formatting_processor = FormattingProcessor()
document_processor = DocumentProcessor()

# Ensure upload directories exist
for folder in ['original', 'processed', 'previews']:
    Path(os.path.join(app.config['UPLOAD_FOLDER'], folder)).mkdir(parents=True, exist_ok=True)

# Routes
@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = db_handler.get_user_by_email(email)
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['name'] = user.get('name', 'User')
            session['user_type'] = user.get('user_type', 'free')
            
            # Update last login
            db_handler.update_last_login(user['id'])
            
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        user_type = request.form.get('user_type', 'student')
        
        # Validation
        if not all([name, email, password]):
            flash('All fields are required', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        if db_handler.get_user_by_email(email):
            flash('Email already registered', 'danger')
            return render_template('register.html')
        
        # Create user
        user_id = db_handler.create_user(
            name=name,
            email=email,
            password=password,
            user_type=user_type
        )
        
        if user_id:
            session['user_id'] = user_id
            session['email'] = email
            session['name'] = name
            session['user_type'] = user_type
            
            flash('Registration successful! Welcome to ScholarFix!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Registration failed. Please try again.', 'danger')
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    user_id = session['user_id']
    
    # Get user info
    user = db_handler.get_user_by_id(user_id)
    
    # Get user's recent documents
    documents = db_handler.get_user_documents(user_id, limit=10)
    
    # Get usage statistics
    stats = db_handler.get_user_stats(user_id)
    
    return render_template('dashboard.html', 
                         user=user, 
                         documents=documents,
                         stats=stats)

@app.route('/process', methods=['POST'])
@login_required
def process_document():
    """Process uploaded document"""
    try:
        user_id = session['user_id']
        
        # Check file in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        if not file_handler.allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Use .docx or .pdf'}), 400
        
        # Get processing options
        mode = request.form.get('mode', 'academic')
        options = {
            'grammar': request.form.get('grammar', 'true') == 'true',
            'clarity': request.form.get('clarity', 'true') == 'true',
            'tone': request.form.get('tone', 'true') == 'true',
            'formatting': request.form.get('formatting', 'true') == 'true',
            'citation_style': request.form.get('citation_style', 'apa')
        }
        
        # Save original file
        file_id = str(uuid.uuid4())
        original_path = file_handler.save_file(file, file_id, 'original')
        
        # Create document record
        doc_id = db_handler.create_document(
            user_id=user_id,
            file_id=file_id,
            original_filename=secure_filename(file.filename),
            mode=mode,
            options=json.dumps(options)
        )
        
        # Start processing (async in production)
        result = document_processor.process_document(
            original_path=original_path,
            mode=mode,
            options=options,
            file_id=file_id
        )
        
        # Save processed document
        processed_path = file_handler.save_processed_content(
            file_id=file_id,
            content=result['processed_text'],
            metadata=result.get('metadata', {})
        )
        
        # Update document record
        db_handler.update_document_processing(
            doc_id=doc_id,
            status='completed',
            metrics=json.dumps(result.get('metrics', {})),
            processed_path=processed_path
        )
        
        # Save preview data
        preview_data = {
            'original': result.get('original_text', '')[:500],
            'processed': result.get('processed_text', '')[:500],
            'changes': result.get('changes', {})
        }
        file_handler.save_preview(file_id, preview_data)
        
        return jsonify({
            'success': True,
            'doc_id': doc_id,
            'file_id': file_id,
            'preview': preview_data,
            'metrics': result.get('metrics', {}),
            'download_url': url_for('download_document', file_id=file_id)
        })
        
    except Exception as e:
        app.logger.error(f'Processing error: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/download/<file_id>')
@login_required
def download_document(file_id):
    """Download processed document"""
    try:
        user_id = session['user_id']
        
        # Verify document ownership
        document = db_handler.get_document_by_file_id(file_id)
        if not document or document['user_id'] != user_id:
            flash('Document not found or access denied', 'danger')
            return redirect(url_for('dashboard'))
        
        # Get processed file path
        file_path = document.get('processed_path')
        if not file_path or not os.path.exists(file_path):
            flash('Processed file not available', 'danger')
            return redirect(url_for('dashboard'))
        
        # Determine filename
        original_name = document['original_filename']
        name, ext = os.path.splitext(original_name)
        download_name = f"scholarfix_{name}_refined{ext}"
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=download_name
        )
        
    except Exception as e:
        app.logger.error(f'Download error: {str(e)}')
        flash('Download failed', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/preview/<file_id>')
@login_required
def preview_document(file_id):
    """Get document preview"""
    try:
        user_id = session['user_id']
        
        # Verify document ownership
        document = db_handler.get_document_by_file_id(file_id)
        if not document or document['user_id'] != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Load preview data
        preview_data = file_handler.load_preview(file_id)
        
        return jsonify({
            'success': True,
            'preview': preview_data,
            'document': {
                'id': document['id'],
                'original_filename': document['original_filename'],
                'mode': document['mode'],
                'created_at': document['created_at'],
                'status': document['status']
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/documents')
@login_required
def get_documents():
    """Get user's documents"""
    try:
        user_id = session['user_id']
        documents = db_handler.get_user_documents(user_id)
        
        return jsonify({
            'success': True,
            'documents': documents
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/document/<doc_id>')
@login_required
def get_document(doc_id):
    """Get specific document"""
    try:
        user_id = session['user_id']
        document = db_handler.get_document(doc_id)
        
        if not document or document['user_id'] != user_id:
            return jsonify({'error': 'Document not found'}), 404
        
        # Load metrics if available
        metrics = {}
        if document.get('metrics'):
            try:
                metrics = json.loads(document['metrics'])
            except:
                pass
        
        return jsonify({
            'success': True,
            'document': document,
            'metrics': metrics
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    user = db_handler.get_user_by_id(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        user_id = session['user_id']
        name = request.form.get('name')
        
        if name:
            db_handler.update_user(user_id, name=name)
            session['name'] = name
            flash('Profile updated successfully', 'success')
        
    except Exception as e:
        flash('Failed to update profile', 'danger')
    
    return redirect(url_for('profile'))

# API Routes for external integration
@app.route('/api/v1/process', methods=['POST'])
def api_process_document():
    """API endpoint for document processing"""
    # Check API key
    api_key = request.headers.get('X-API-Key')
    if not api_key or not db_handler.verify_api_key(api_key):
        return jsonify({'error': 'Invalid API key'}), 401
    
    # Get user from API key
    user = db_handler.get_user_by_api_key(api_key)
    if not user:
        return jsonify({'error': 'Invalid API key'}), 401
    
    # Process document (similar to /process route)
    # ... (implementation similar to /process route)
    
    return jsonify({'message': 'API endpoint'})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}')
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Create database tables if they don't exist
    db_handler.init_db()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)