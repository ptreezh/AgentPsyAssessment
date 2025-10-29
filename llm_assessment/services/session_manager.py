"""
Session Manager Module
Manages isolated question processing sessions for LLM assessments
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime


class Session:
    """
    Represents an isolated assessment session for a single question
    """
    
    def __init__(self, question_id: str, metadata: Dict[str, Any] = None):
        """
        Initialize a new session
        
        Args:
            question_id: Unique identifier for the question
            metadata: Additional session metadata
        """
        self.session_id = str(uuid.uuid4())
        self.question_id = question_id
        self.created_at = datetime.now().isoformat()
        self.metadata = metadata or {}
        self.conversation_history = []
        self.is_active = True
    
    def add_turn(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """
        Add a conversation turn to the session
        
        Args:
            role: Role of the speaker (system, user, assistant)
            content: Content of the message
            metadata: Additional metadata for the turn
        """
        turn = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        self.conversation_history.append(turn)
    
    def get_conversation(self) -> list:
        """Get the complete conversation history"""
        return self.conversation_history.copy()
    
    def get_last_turn(self) -> Optional[Dict[str, Any]]:
        """Get the last conversation turn"""
        if not self.conversation_history:
            return None
        return self.conversation_history[-1]
    
    def close(self):
        """Close the session"""
        self.is_active = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for logging"""
        return {
            "session_id": self.session_id,
            "question_id": self.question_id,
            "created_at": self.created_at,
            "is_active": self.is_active,
            "metadata": self.metadata,
            "conversation_history": self.conversation_history
        }


class SessionManager:
    """
    Manages isolated question processing sessions for LLM assessments
    """
    
    def __init__(self):
        """Initialize SessionManager"""
        self.active_sessions: Dict[str, Session] = {}
        self.completed_sessions: Dict[str, Session] = {}
    
    def create_session(self, question_id: str, metadata: Dict[str, Any] = None) -> Session:
        """
        Create a new isolated session for a question
        
        Args:
            question_id: Unique identifier for the question
            metadata: Additional session metadata
            
        Returns:
            New Session instance
        """
        session = Session(question_id, metadata)
        self.active_sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get a session by ID
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session instance or None if not found
        """
        return self.active_sessions.get(session_id) or self.completed_sessions.get(session_id)
    
    def close_session(self, session_id: str) -> bool:
        """
        Close a session and move it to completed
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session was closed, False if not found
        """
        session = self.active_sessions.get(session_id)
        if session:
            session.close()
            self.completed_sessions[session_id] = session
            del self.active_sessions[session_id]
            return True
        return False
    
    def cleanup_session(self, session_id: str) -> bool:
        """
        Completely remove a session from memory
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session was removed, False if not found
        """
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return True
        elif session_id in self.completed_sessions:
            del self.completed_sessions[session_id]
            return True
        return False
    
    def get_active_sessions(self) -> Dict[str, Session]:
        """Get all active sessions"""
        return self.active_sessions.copy()
    
    def get_completed_sessions(self) -> Dict[str, Session]:
        """Get all completed sessions"""
        return self.completed_sessions.copy()
    
    def get_session_count(self) -> int:
        """Get total number of sessions (active + completed)"""
        return len(self.active_sessions) + len(self.completed_sessions)
    
    def cleanup_all_sessions(self):
        """Clean up all sessions"""
        self.active_sessions.clear()
        self.completed_sessions.clear()
    
    def validate_session_isolation(self) -> Dict[str, Any]:
        """
        Validate that sessions are properly isolated
        
        Returns:
            Validation result with status and details
        """
        validation = {
            "valid": True,
            "issues": [],
            "active_sessions": len(self.active_sessions),
            "completed_sessions": len(self.completed_sessions),
            "duplicate_question_ids": []
        }
        
        # Check for duplicate question IDs in active sessions
        question_ids = {}
        for session_id, session in self.active_sessions.items():
            qid = session.question_id
            if qid in question_ids:
                validation["valid"] = False
                validation["issues"].append(f"Duplicate question ID: {qid}")
                validation["duplicate_question_ids"].append(qid)
            question_ids[qid] = session_id
        
        return validation
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get summary of all sessions
        
        Returns:
            Summary information about sessions
        """
        return {
            "total_sessions": self.get_session_count(),
            "active_sessions": len(self.active_sessions),
            "completed_sessions": len(self.completed_sessions),
            "active_session_ids": list(self.active_sessions.keys()),
            "completed_session_ids": list(self.completed_sessions.keys())
        }