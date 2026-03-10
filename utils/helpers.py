"""
Helper functions for ScholarFix
"""

import re
import uuid
import hashlib
import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

def format_date(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format date string"""
    try:
        if isinstance(date_str, str):
            # Try to parse ISO format
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        else:
            dt = date_str
        
        return dt.strftime(format_str)
    except:
        return str(date_str)

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def validate_email(email: str) -> bool:
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    validation = {
        'valid': True,
        'errors': [],
        'score': 0
    }
    
    # Check length
    if len(password) < 8:
        validation['valid'] = False
        validation['errors'].append('Password must be at least 8 characters long')
    
    # Check for uppercase
    if not any(c.isupper() for c in password):
        validation['score'] += 1
        validation['errors'].append('Add uppercase letters for better security')
    
    # Check for lowercase
    if not any(c.islower() for c in password):
        validation['score'] += 1
        validation['errors'].append('Add lowercase letters')
    
    # Check for digits
    if not any(c.isdigit() for c in password):
        validation['score'] += 1
        validation['errors'].append('Add numbers')
    
    # Check for special characters
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?`~' for c in password):
        validation['score'] += 1
        validation['errors'].append('Add special characters')
    
    # Calculate final score
    validation['score'] = max(0, 5 - validation['score'])
    
    return validation

def generate_api_key(length: int = 32) -> str:
    """Generate API key"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_secure_token() -> str:
    """Generate secure token"""
    return str(uuid.uuid4()) + hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:16]

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal"""
    # Remove directory components
    filename = os.path.basename(filename)
    # Remove null bytes
    filename = filename.replace('\x00', '')
    # Replace problematic characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255 - len(ext)] + ext
    return filename

def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def calculate_readability_score(text: str) -> Dict[str, Any]:
    """Calculate readability score (simplified)"""
    if not text:
        return {'score': 0, 'level': 'Unknown'}
    
    # Count sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Count words
    words = re.findall(r'\b\w+\b', text)
    
    if not sentences or not words:
        return {'score': 0, 'level': 'Unknown'}
    
    # Calculate average sentence length
    avg_sentence_length = len(words) / len(sentences)
    
    # Calculate average word length
    avg_word_length = sum(len(word) for word in words) / len(words)
    
    # Simplified readability score
    score = 100 - (avg_sentence_length * 1.5) - (avg_word_length * 10)
    score = max(0, min(100, score))
    
    # Determine level
    if score >= 80:
        level = 'Very Easy'
    elif score >= 70:
        level = 'Easy'
    elif score >= 60:
        level = 'Fairly Easy'
    elif score >= 50:
        level = 'Standard'
    elif score >= 30:
        level = 'Difficult'
    else:
        level = 'Very Difficult'
    
    return {
        'score': round(score, 1),
        'level': level,
        'avg_sentence_length': round(avg_sentence_length, 1),
        'avg_word_length': round(avg_word_length, 1)
    }

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def generate_document_metrics(original: str, processed: str) -> Dict[str, Any]:
    """Generate document comparison metrics"""
    original_words = original.split()
    processed_words = processed.split()
    
    original_chars = len(original)
    processed_chars = len(processed)
    
    return {
        'word_count': {
            'original': len(original_words),
            'processed': len(processed_words),
            'change': len(processed_words) - len(original_words),
            'change_percentage': round(((len(processed_words) - len(original_words)) / len(original_words) * 100), 1) if original_words else 0
        },
        'character_count': {
            'original': original_chars,
            'processed': processed_chars,
            'change': processed_chars - original_chars
        },
        'avg_word_length': {
            'original': round(sum(len(w) for w in original_words) / len(original_words), 1) if original_words else 0,
            'processed': round(sum(len(w) for w in processed_words) / len(processed_words), 1) if processed_words else 0
        }
    }

def is_valid_uuid(uuid_str: str) -> bool:
    """Check if string is valid UUID"""
    try:
        uuid.UUID(uuid_str)
        return True
    except ValueError:
        return False

def get_time_ago(dt: datetime) -> str:
    """Get human-readable time ago string"""
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "just now"