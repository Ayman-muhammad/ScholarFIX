"""
File handling utilities for ScholarFix
"""

import os
import uuid
import json
import shutil
from pathlib import Path
from werkzeug.utils import secure_filename
from typing import Dict, Any, Optional, Tuple

class FileHandler:
    def __init__(self, base_upload_folder: str = 'uploads'):
        """Initialize file handler"""
        self.base_upload_folder = base_upload_folder
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all necessary directories exist"""
        directories = ['original', 'processed', 'previews', 'temp']
        for directory in directories:
            Path(os.path.join(self.base_upload_folder, directory)).mkdir(parents=True, exist_ok=True)
    
    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        allowed_extensions = {'docx', 'pdf', 'txt'}
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    def save_file(self, file, file_id: str, file_type: str = 'original') -> str:
        """
        Save uploaded file
        
        Args:
            file: Uploaded file object
            file_id: Unique file identifier
            file_type: Type of file (original, processed, preview)
            
        Returns:
            Path to saved file
        """
        # Secure filename
        filename = secure_filename(file.filename)
        extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        # Generate new filename with file_id
        new_filename = f"{file_id}_{filename}" if file_type == 'original' else f"{file_id}.{extension}"
        
        # Determine save path
        save_folder = os.path.join(self.base_upload_folder, file_type)
        save_path = os.path.join(save_folder, new_filename)
        
        # Save file
        file.save(save_path)
        
        return save_path
    
    def save_processed_content(self, file_id: str, content: str, metadata: Dict = None) -> str:
        """
        Save processed document content
        
        Args:
            file_id: File identifier
            content: Processed text content
            metadata: Additional metadata
            
        Returns:
            Path to saved file
        """
        # Create processed file path
        save_folder = os.path.join(self.base_upload_folder, 'processed')
        save_path = os.path.join(save_folder, f"{file_id}.txt")
        
        # Prepare content with metadata
        file_content = ""
        if metadata:
            file_content += f"METADATA:\n{json.dumps(metadata, indent=2)}\n\n"
            file_content += "=" * 50 + "\n\n"
        
        file_content += content
        
        # Save to file
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        return save_path
    
    def save_preview(self, file_id: str, preview_data: Dict) -> str:
        """
        Save preview data
        
        Args:
            file_id: File identifier
            preview_data: Preview data dictionary
            
        Returns:
            Path to saved preview file
        """
        preview_path = os.path.join(self.base_upload_folder, 'previews', f"{file_id}.json")
        
        with open(preview_path, 'w', encoding='utf-8') as f:
            json.dump(preview_data, f, indent=2)
        
        return preview_path
    
    def load_preview(self, file_id: str) -> Optional[Dict]:
        """
        Load preview data
        
        Args:
            file_id: File identifier
            
        Returns:
            Preview data dictionary or None
        """
        preview_path = os.path.join(self.base_upload_folder, 'previews', f"{file_id}.json")
        
        if os.path.exists(preview_path):
            try:
                with open(preview_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        
        return None
    
    def get_file_path(self, file_id: str, file_type: str = 'processed') -> Optional[str]:
        """
        Get path to file
        
        Args:
            file_id: File identifier
            file_type: Type of file
            
        Returns:
            File path or None if not found
        """
        folder = os.path.join(self.base_upload_folder, file_type)
        
        # Look for file with this file_id
        for filename in os.listdir(folder):
            if filename.startswith(file_id):
                return os.path.join(folder, filename)
        
        return None
    
    def delete_file(self, file_id: str, file_type: str = 'original') -> bool:
        """
        Delete file
        
        Args:
            file_id: File identifier
            file_type: Type of file
            
        Returns:
            True if deleted, False otherwise
        """
        file_path = self.get_file_path(file_id, file_type)
        
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except:
                return False
        
        return False
    
    def cleanup_old_files(self, days_old: int = 7):
        """Clean up files older than specified days"""
        import time
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.now() - timedelta(days=days_old)
        
        for file_type in ['original', 'processed', 'previews', 'temp']:
            folder = os.path.join(self.base_upload_folder, file_type)
            
            if not os.path.exists(folder):
                continue
            
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_time:
                        os.remove(file_path)
                except:
                    continue
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information about a file
        
        Args:
            file_path: Path to file
            
        Returns:
            File information dictionary
        """
        if not os.path.exists(file_path):
            return {}
        
        file_stats = os.stat(file_path)
        
        return {
            'filename': os.path.basename(file_path),
            'size': file_stats.st_size,
            'size_human': self._format_size(file_stats.st_size),
            'created': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
            'extension': os.path.splitext(file_path)[1].lower().replace('.', ''),
            'path': file_path
        }
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def extract_text_from_file(self, file_path: str) -> Tuple[str, Dict]:
        """
        Extract text from document file (simplified version)
        
        Note: In production, implement proper extraction for different file types
        
        Args:
            file_path: Path to document file
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        metadata = {
            'filename': os.path.basename(file_path),
            'extension': os.path.splitext(file_path)[1].lower(),
            'size': os.path.getsize(file_path)
        }
        
        try:
            # For .txt files
            if file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    metadata['encoding'] = 'utf-8'
                    return text, metadata
            
            # For other file types, return placeholder
            # In production, implement proper extraction using:
            # - python-docx for .docx
            # - PyPDF2 for .pdf
            # - Other libraries for other formats
            
            text = f"Placeholder text for {metadata['filename']}. "
            text += "In production, implement proper text extraction."
            
            return text, metadata
            
        except Exception as e:
            metadata['error'] = str(e)
            return f"Error extracting text: {str(e)}", metadata

# Helper function for Flask
def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed (Flask helper)"""
    allowed_extensions = {'docx', 'pdf', 'txt'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions