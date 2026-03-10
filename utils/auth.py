"""
Authentication utilities for ScholarFix
"""

from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def user_type_required(user_type):
    """Decorator to require specific user type"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_type' not in session:
                flash('Please log in', 'warning')
                return redirect(url_for('login'))
            
            if session['user_type'] != user_type:
                flash('Access denied. Insufficient privileges.', 'danger')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def generate_token(user_id):
    """Generate a simple token for API access"""
    import hashlib
    import time
    
    timestamp = str(int(time.time()))
    data = f"{user_id}:{timestamp}:scholarfix-secret"
    return hashlib.sha256(data.encode()).hexdigest()

def verify_token(token, user_id):
    """Verify API token"""
    import hashlib
    import time
    
    # Check if token is valid within 24 hours
    current_time = int(time.time())
    
    for i in range(24 * 60):  # Check each minute for 24 hours
        check_time = current_time - (i * 60)
        data = f"{user_id}:{check_time}:scholarfix-secret"
        if hashlib.sha256(data.encode()).hexdigest() == token:
            return True
    
    return False

def get_current_user():
    """Get current user from session"""
    from flask import session
    return {
        'id': session.get('user_id'),
        'email': session.get('email'),
        'name': session.get('name'),
        'user_type': session.get('user_type')
    }