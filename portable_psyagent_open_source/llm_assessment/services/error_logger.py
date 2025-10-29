"""
Error Logger Service
Handles independent error logging for robust assessment execution.
"""

import os
import json
import traceback
import sys
from datetime import datetime
from typing import Dict, Any, List, Tuple


class ErrorLogEntry:
    """Error log entry structure"""
    
    def __init__(self, error: Exception, context: Dict[str, Any] = None):
        self.timestamp = datetime.now().isoformat()
        self.error_type = type(error).__name__
        self.message = str(error)
        self.stack_trace = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        self.context = context or {}


class ErrorLogger:
    """Independent error logger for assessment system"""
    
    def __init__(self, log_dir: str = "logs/errors"):
        """
        Initialize error logger.
        
        Args:
            log_dir: Directory to store error logs
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None) -> str:
        """
        Log an error to a daily JSONL file.
        
        Args:
            error: The exception to log
            context: Additional context information
            
        Returns:
            Path to the log file
        """
        # Create daily log file
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(self.log_dir, f"{date_str}.jsonl")
        
        # Create log entry
        entry = ErrorLogEntry(error, context)
        
        # Write to file
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry.__dict__, ensure_ascii=False) + '\n')
        except Exception as e:
            # If we can't write to the log file, print to stderr
            print(f"Failed to write to error log: {e}", file=sys.stderr)
        
        return log_file
    
    def get_error_summary(self, date_range: Tuple[datetime, datetime] = None) -> List[Dict[str, Any]]:
        """
        Get error summary for a date range.
        
        Args:
            date_range: Tuple of (start_date, end_date). If None, uses last 7 days.
            
        Returns:
            List of error summary entries
        """
        if date_range is None:
            end_date = datetime.now()
            start_date = end_date.replace(day=end_date.day - 7)
            date_range = (start_date, end_date)
        
        summary = []
        # Implementation would read log files and aggregate data
        # This is a simplified placeholder
        return summary


# Example usage:
# logger = ErrorLogger()
# 
# try:
#     # Some operation that might fail
#     pass
# except Exception as e:
#     logger.log_error(e, {"operation": "test_operation", "model": "test_model"})