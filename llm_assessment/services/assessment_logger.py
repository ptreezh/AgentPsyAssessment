"""
Assessment Logger Service
Handles logging for assessment execution, including system output, warnings, errors, and model responses.
"""

import os
import json
import traceback
import sys
from datetime import datetime
from typing import Dict, Any, List


class AssessmentLogEntry:
    """Assessment log entry structure"""
    
    def __init__(self, message: str, level: str = "INFO", context: Dict[str, Any] = None):
        self.timestamp = datetime.now().isoformat()
        self.level = level
        self.message = message
        self.context = context or {}


class AssessmentLogger:
    """Independent logger for assessment system"""
    
    def __init__(self, log_dir: str = "logs/assessments"):
        """
        Initialize assessment logger.
        
        Args:
            log_dir: Directory to store assessment logs
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.current_log_file = None
    
    def start_new_log(self, model: str, test_name: str, role_name: str) -> str:
        """
        Start a new log file for an assessment run.
        
        Args:
            model: Model identifier
            test_name: Test name
            role_name: Role name
            
        Returns:
            Path to the log file
        """
        # Create log file with timestamp and assessment info
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_str = str(model) if model else "unknown_model"
        test_name_str = str(test_name) if test_name else "unknown_test"
        role_name_str = str(role_name) if role_name else "default"
        
        # Sanitize strings for filename
        model_str = model_str.replace('/', '_').replace('\\', '_').replace(':', '_')
        test_name_str = test_name_str.replace('/', '_').replace('\\', '_').replace(':', '_')
        role_name_str = role_name_str.replace('/', '_').replace('\\', '_').replace(':', '_')
        
        log_filename = f"assessment_{model_str}_{test_name_str}_{role_name_str}_{timestamp}.log"
        self.current_log_file = os.path.join(self.log_dir, log_filename)
        
        # Write header to log file
        header = {
            "timestamp": datetime.now().isoformat(),
            "model": model_str,
            "test_name": test_name_str,
            "role_name": role_name_str,
            "log_file": self.current_log_file
        }
        
        try:
            with open(self.current_log_file, 'w', encoding='utf-8') as f:
                f.write(f"=== Assessment Log ===\n")
                f.write(f"Start Time: {header['timestamp']}\n")
                f.write(f"Model: {header['model']}\n")
                f.write(f"Test: {header['test_name']}\n")
                f.write(f"Role: {header['role_name']}\n")
                f.write("=" * 50 + "\n\n")
        except Exception as e:
            print(f"Failed to create log file: {e}", file=sys.stderr)
        
        return self.current_log_file
    
    def log(self, message: str, level: str = "INFO", context: Dict[str, Any] = None):
        """
        Log a message to the current log file.
        
        Args:
            message: Message to log
            level: Log level (INFO, WARNING, ERROR, DEBUG)
            context: Additional context information
        """
        if not self.current_log_file:
            print(f"Log message before log file initialized: {message}", file=sys.stderr)
            return
            
        # Create log entry
        entry = AssessmentLogEntry(message, level, context)
        
        # Write to file
        try:
            with open(self.current_log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{entry.timestamp}] {entry.level}: {entry.message}\n")
                if entry.context:
                    f.write(f"Context: {json.dumps(entry.context, ensure_ascii=False, indent=2)}\n")
                f.write("\n")
        except Exception as e:
            # If we can't write to the log file, print to stderr
            print(f"Failed to write to assessment log: {e}", file=sys.stderr)
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None) -> str:
        """
        Log an error with full traceback.
        
        Args:
            error: The exception to log
            context: Additional context information
            
        Returns:
            Path to the log file
        """
        # Create error entry with full traceback
        entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "message": str(error),
            "stack_trace": ''.join(traceback.format_exception(type(error), error, error.__traceback__)),
            "context": context or {}
        }
        
        # Write to file
        if self.current_log_file:
            try:
                with open(self.current_log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{entry.timestamp}] ERROR: {entry.error_type}: {entry.message}\n")
                    f.write(f"Stack Trace:\n{entry.stack_trace}\n")
                    if entry.context:
                        f.write(f"Context: {json.dumps(entry.context, ensure_ascii=False, indent=2)}\n")
                    f.write("\n")
            except Exception as e:
                # If we can't write to the log file, print to stderr
                print(f"Failed to write error to assessment log: {e}", file=sys.stderr)
        
        return self.current_log_file
    
    def log_model_response(self, response: str, prompt: str = None, context: Dict[str, Any] = None, session_id: str = None):
        """
        Log model response with optional prompt in JSON format.
        
        Args:
            response: Model response
            prompt: Prompt that generated the response
            context: Additional context information
            session_id: Unique session identifier for isolation
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id or "default",
            "level": "RESPONSE",
            "prompt": prompt,
            "response": response,
            "context": context or {}
        }
        
        if not self.current_log_file:
            print(f"Log message before log file initialized: {json.dumps(log_entry, ensure_ascii=False)}", file=sys.stderr)
            return
            
        try:
            with open(self.current_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"Failed to write model response to log: {e}", file=sys.stderr)
    
    def log_llm_interaction(self, session_id: str, prompt: str, response: str, metadata: Dict[str, Any] = None):
        """
        Log complete LLM interaction with session isolation.
        
        Args:
            session_id: Unique session identifier
            prompt: LLM input prompt
            response: LLM output response
            metadata: Additional metadata (temperature, stress_level, etc.)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "type": "llm_interaction",
            "prompt": prompt,
            "response": response,
            "metadata": metadata or {}
        }
        
        if not self.current_log_file:
            print(f"LLM interaction log: {json.dumps(log_entry, ensure_ascii=False)}", file=sys.stderr)
            return
            
        try:
            with open(self.current_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                f.flush()  # Ensure content is written to disk
        except Exception as e:
            print(f"Failed to write LLM interaction to log: {e}", file=sys.stderr)
    
    def log_complete_session(self, session_id: str, conversation: list, extracted_response: str, metadata: Dict[str, Any] = None):
        """
        Log complete session with full conversation and extracted response.
        
        Args:
            session_id: Unique session identifier
            conversation: Complete conversation history
            extracted_response: Final extracted response
            metadata: Additional metadata
        """
        # 只记录元数据和提取的响应，不记录完整的对话历史
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "type": "complete_session",
            "extracted_response": extracted_response,
            "metadata": metadata or {}
        }
        
        if not self.current_log_file:
            print(f"Session log: {json.dumps(log_entry, ensure_ascii=False)}", file=sys.stderr)
            return
            
        try:
            with open(self.current_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False, indent=2) + '\n')
                f.flush()  # Ensure content is written to disk
        except Exception as e:
            print(f"Failed to write session log: {e}", file=sys.stderr)
