"""
Encoding Manager Service
Handles encoding issues for robust assessment execution, particularly for Chinese characters.
"""

import os
import codecs
from typing import Optional, List


class EncodingManager:
    """Manages encoding for file operations, with special handling for Chinese characters"""
    
    DEFAULT_ENCODING = 'utf-8'
    FALLBACK_ENCODINGS = ['gbk', 'gb2312', 'utf-8-sig']
    
    def __init__(self, encoding: str = DEFAULT_ENCODING, fallback_encodings: List[str] = None):
        """
        Initialize encoding manager.
        
        Args:
            encoding: Default encoding to use
            fallback_encodings: List of fallback encodings to try if default fails
        """
        self.encoding = encoding
        self.fallback_encodings = fallback_encodings or self.FALLBACK_ENCODINGS
    
    def safe_read(self, file_path: str) -> Optional[str]:
        """
        Safely read a file with encoding detection.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            File content as string, or None if reading failed
        """
        # Try default encoding first
        try:
            with open(file_path, 'r', encoding=self.encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            pass
        
        # Try fallback encodings
        for encoding in self.fallback_encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    # Convert to UTF-8 for consistency
                    return content
            except UnicodeDecodeError:
                continue
        
        # If all encodings fail, try with automatic detection
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            detected_encoding = self._detect_encoding(raw_data)
            if detected_encoding:
                return raw_data.decode(detected_encoding)
        except Exception:
            pass
        
        # If everything fails, return None
        return None
    
    def safe_write(self, file_path: str, content: str) -> bool:
        """
        Safely write content to a file with UTF-8 encoding.
        
        Args:
            file_path: Path to the file to write
            content: Content to write
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write with UTF-8 encoding
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception:
            return False
    
    def _detect_encoding(self, raw_data: bytes) -> Optional[str]:
        """
        Detect encoding of raw bytes data.
        
        Args:
            raw_data: Raw bytes data
            
        Returns:
            Detected encoding or None
        """
        # Try common encodings
        for encoding in [self.encoding] + self.fallback_encodings:
            try:
                raw_data.decode(encoding)
                return encoding
            except UnicodeDecodeError:
                continue
        
        # Use chardet if available (optional dependency)
        try:
            import chardet
            result = chardet.detect(raw_data)
            if result['confidence'] > 0.7:
                return result['encoding']
        except ImportError:
            pass
        
        return None


# Example usage:
# encoding_manager = EncodingManager()
# 
# # Read a file with automatic encoding detection
# content = encoding_manager.safe_read("test_file.txt")
# if content:
#     print("File read successfully")
# else:
#     print("Failed to read file with any encoding")
# 
# # Write content with UTF-8 encoding
# success = encoding_manager.safe_write("output.txt", "你好，世界")
# if success:
#     print("File written successfully")
# else:
#     print("Failed to write file")