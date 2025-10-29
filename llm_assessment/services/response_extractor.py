"""
Response Extractor Service
Extracts final assessment responses from multi-turn conversations
"""

import re
from typing import List, Dict, Any, Optional


class ResponseExtractor:
    """
    Service to extract final assessment responses from multi-turn conversations.
    Handles both single-turn and multi-turn conversations with context injection.
    """
    
    ASSESSMENT_MARKER = "[ASSESSMENT_QUESTION]"
    
    def __init__(self):
        """Initialize ResponseExtractor"""
        pass
    
    def extract_final_response(self, conversation: List[Dict[str, Any]]) -> Optional[str]:
        """
        Extract the final response to the assessment question from a conversation.
        
        Args:
            conversation: List of conversation turns with 'role' and 'content' keys
            
        Returns:
            The final response to the assessment question, or None if not found
        """
        if not conversation:
            return None
        
        # Find the last assessment question
        last_assessment_index = self._find_last_assessment_question(conversation)
        
        if last_assessment_index is not None:
            # Find the assistant response to this question
            return self._find_assistant_response(conversation, last_assessment_index)
        else:
            # Fallback: find the last assistant response
            return self._find_last_assistant_response(conversation)
    
    def _find_last_assessment_question(self, conversation: List[Dict[str, Any]]) -> Optional[int]:
        """
        Find the index of the last assessment question in the conversation.
        
        Args:
            conversation: List of conversation turns
            
        Returns:
            Index of the last assessment question, or None if not found
        """
        for i in range(len(conversation) - 1, -1, -1):
            turn = conversation[i]
            if turn.get("role") == "user" and self.ASSESSMENT_MARKER in str(turn.get("content", "")):
                return i
        
        # If no marker found, look for the last user message
        for i in range(len(conversation) - 1, -1, -1):
            turn = conversation[i]
            if turn.get("role") == "user":
                return i
        
        return None
    
    def _find_assistant_response(self, conversation: List[Dict[str, Any]], question_index: int) -> Optional[str]:
        """
        Find the assistant response to a specific question.
        
        Args:
            conversation: List of conversation turns
            question_index: Index of the question
            
        Returns:
            The assistant's response to the question, or None if not found
        """
        # Look for the next assistant response after the question
        for i in range(question_index + 1, len(conversation)):
            turn = conversation[i]
            if turn.get("role") == "assistant":
                return str(turn.get("content", "")).strip()
        
        return None
    
    def _find_last_assistant_response(self, conversation: List[Dict[str, Any]]) -> Optional[str]:
        """
        Find the last assistant response in the conversation.
        
        Args:
            conversation: List of conversation turns
            
        Returns:
            The last assistant response, or None if not found
        """
        for turn in reversed(conversation):
            if turn.get("role") == "assistant":
                return str(turn.get("content", "")).strip()
        
        return None
    
    def add_assessment_marker(self, question: str) -> str:
        """
        Add assessment marker to a question for easier extraction.
        
        Args:
            question: The assessment question
            
        Returns:
            Question with assessment marker added
        """
        if self.ASSESSMENT_MARKER in question:
            return question
        return f"{self.ASSESSMENT_MARKER} {question}"
    
    def is_assessment_question(self, content: str) -> bool:
        """
        Check if content contains an assessment question marker.
        
        Args:
            content: Content to check
            
        Returns:
            True if content contains assessment marker, False otherwise
        """
        return self.ASSESSMENT_MARKER in str(content)
    
    def extract_question_text(self, content: str) -> str:
        """
        Extract the actual question text without the assessment marker.
        
        Args:
            content: Content that may contain assessment marker
            
        Returns:
            Clean question text without marker
        """
        if not content:
            return ""
        
        # Remove assessment marker
        content = str(content)
        if self.ASSESSMENT_MARKER in content:
            return content.replace(self.ASSESSMENT_MARKER, "").strip()
        
        return content.strip()
    
    def validate_conversation_structure(self, conversation: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate the conversation structure for assessment extraction.
        
        Args:
            conversation: List of conversation turns
            
        Returns:
            Validation result with status and details
        """
        validation_result = {
            "valid": True,
            "issues": [],
            "assessment_questions": 0,
            "assistant_responses": 0,
            "structure": "unknown"
        }
        
        if not conversation:
            validation_result["valid"] = False
            validation_result["issues"].append("Empty conversation")
            return validation_result
        
        # Count assessment questions
        assessment_questions = 0
        for turn in conversation:
            if turn.get("role") == "user" and self.is_assessment_question(str(turn.get("content", ""))):
                assessment_questions += 1
        
        validation_result["assessment_questions"] = assessment_questions
        
        # Count assistant responses
        assistant_responses = sum(1 for turn in conversation if turn.get("role") == "assistant")
        validation_result["assistant_responses"] = assistant_responses
        
        # Determine structure type
        if assessment_questions == 1 and assistant_responses == 1:
            validation_result["structure"] = "single_turn"
        elif assessment_questions >= 1 and assistant_responses >= 1:
            validation_result["structure"] = "multi_turn"
        else:
            validation_result["structure"] = "incomplete"
            validation_result["issues"].append("Missing assessment question or response")
        
        return validation_result