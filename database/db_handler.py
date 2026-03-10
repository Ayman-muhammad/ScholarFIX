"""
Database operations for ScholarFix
"""

import sqlite3
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

class DatabaseHandler:
    def __init__(self, db_path):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                user_type TEXT DEFAULT 'free',
                api_key TEXT UNIQUE,
                documents_count INTEGER DEFAULT 0,
                max_documents INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                file_id TEXT UNIQUE NOT NULL,
                original_filename TEXT NOT NULL,
                processed_filename TEXT,
                mode TEXT DEFAULT 'academic',
                options TEXT,
                status TEXT DEFAULT 'processing',
                metrics TEXT,
                original_path TEXT,
                processed_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # User stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id INTEGER PRIMARY KEY,
                total_documents INTEGER DEFAULT 0,
                total_words INTEGER DEFAULT 0,
                grammar_fixes INTEGER DEFAULT 0,
                last_processed TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # User operations
    def create_user(self, name, email, password, user_type='student'):
        """Create new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Generate API key
            api_key = str(uuid.uuid4())
            
            cursor.execute('''
                INSERT INTO users (name, email, password_hash, user_type, api_key)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, email, generate_password_hash(password), user_type, api_key))
            
            user_id = cursor.lastrowid
            
            # Initialize user stats
            cursor.execute('''
                INSERT OR IGNORE INTO user_stats (user_id) VALUES (?)
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            return user_id
            
        except sqlite3.IntegrityError:
            return None
    
    def get_user_by_email(self, email):
        """Get user by email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        conn.close()
        return dict(user) if user else None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        return dict(user) if user else None
    
    def get_user_by_api_key(self, api_key):
        """Get user by API key"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE api_key = ?', (api_key,))
        user = cursor.fetchone()
        
        conn.close()
        return dict(user) if user else None
    
    def verify_api_key(self, api_key):
        """Verify API key"""
        user = self.get_user_by_api_key(api_key)
        return user is not None
    
    def update_user(self, user_id, **kwargs):
        """Update user information"""
        allowed_fields = ['name', 'user_type', 'max_documents']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values())
        values.append(user_id)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'''
            UPDATE users SET {set_clause} WHERE id = ?
        ''', values)
        
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def update_last_login(self, user_id):
        """Update user's last login time"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
    
    # Document operations
    def create_document(self, user_id, file_id, original_filename, mode='academic', options='{}'):
        """Create document record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO documents (user_id, file_id, original_filename, mode, options)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, file_id, original_filename, mode, options))
        
        doc_id = cursor.lastrowid
        
        # Update user document count
        cursor.execute('''
            UPDATE users SET documents_count = documents_count + 1 WHERE id = ?
        ''', (user_id,))
        
        # Update user stats
        cursor.execute('''
            UPDATE user_stats 
            SET total_documents = total_documents + 1,
                last_processed = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        
        return doc_id
    
    def get_document(self, doc_id):
        """Get document by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
        document = cursor.fetchone()
        
        conn.close()
        return dict(document) if document else None
    
    def get_document_by_file_id(self, file_id):
        """Get document by file ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM documents WHERE file_id = ?', (file_id,))
        document = cursor.fetchone()
        
        conn.close()
        return dict(document) if document else None
    
    def get_user_documents(self, user_id, limit=50):
        """Get all documents for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM documents 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        documents = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return documents
    
    def update_document_processing(self, doc_id, status, metrics=None, processed_path=None):
        """Update document processing status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if metrics:
            metrics_json = json.dumps(metrics)
            cursor.execute('''
                UPDATE documents 
                SET status = ?, metrics = ?, processed_path = ?, processed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, metrics_json, processed_path, doc_id))
        else:
            cursor.execute('''
                UPDATE documents 
                SET status = ?, processed_path = ?, processed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, processed_path, doc_id))
        
        conn.commit()
        conn.close()
    
    def delete_document(self, doc_id, user_id):
        """Delete document"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM documents WHERE id = ? AND user_id = ?
        ''', (doc_id, user_id))
        
        deleted = cursor.rowcount > 0
        
        if deleted:
            # Update user document count
            cursor.execute('''
                UPDATE users SET documents_count = documents_count - 1 WHERE id = ?
            ''', (user_id,))
        
        conn.commit()
        conn.close()
        return deleted
    
    # User stats
    def get_user_stats(self, user_id):
        """Get user statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get basic user info
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = dict(cursor.fetchone())
        
        # Get stats
        cursor.execute('SELECT * FROM user_stats WHERE user_id = ?', (user_id,))
        stats_row = cursor.fetchone()
        stats = dict(stats_row) if stats_row else {}
        
        # Get today's document count
        cursor.execute('''
            SELECT COUNT(*) as today_count 
            FROM documents 
            WHERE user_id = ? AND DATE(created_at) = DATE('now')
        ''', (user_id,))
        today = cursor.fetchone()['today_count']
        
        conn.close()
        
        return {
            'user': user,
            'stats': stats,
            'today_documents': today,
            'documents_left': max(0, user.get('max_documents', 5) - today)
        }
    
    def update_user_stats(self, user_id, grammar_fixes=0, word_count=0):
        """Update user statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_stats 
            SET grammar_fixes = grammar_fixes + ?,
                total_words = total_words + ?,
                last_processed = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (grammar_fixes, word_count, user_id))
        
        conn.commit()
        conn.close()
    
    # Helper methods
    def user_can_upload(self, user_id):
        """Check if user can upload more documents today"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get today's upload count
        cursor.execute('''
            SELECT COUNT(*) as today_count 
            FROM documents 
            WHERE user_id = ? AND DATE(created_at) = DATE('now')
        ''', (user_id,))
        today_count = cursor.fetchone()['today_count']
        
        # Get user's max documents
        cursor.execute('SELECT max_documents FROM users WHERE id = ?', (user_id,))
        max_docs = cursor.fetchone()['max_documents']
        
        conn.close()
        
        return today_count < max_docs