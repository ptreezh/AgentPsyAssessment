"""
Question Failure Handler Service
Handles skipping individual questions when they fail during psychological assessments,
allowing the assessment to continue while recording failure information.
"""

import json
import logging
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime


class QuestionFailureHandler:
    """Manages question-level failure handling in psychological assessments"""
    
    def __init__(self, max_retries_per_question: int = 0, use_fallback: bool = False):
        """
        Initialize question failure handler.
        
        Args:
            max_retries_per_question: Number of retries per question before giving up
            use_fallback: Whether to use fallback mechanisms for failed questions
        """
        self.max_retries_per_question = max_retries_per_question
        self.use_fallback = use_fallback
        self.logger = logging.getLogger('assessment.question')
    
    def process_questions_with_skip(self, questions: List[Dict], llm_client) -> List[Optional[Dict]]:
        """
        Process questions, skipping failed ones and continuing with the rest.
        
        Args:
            questions: List of question dictionaries
            llm_client: LLM client for processing questions
            
        Returns:
            List of results (None for failed questions)
        """
        results = []
        
        for question in questions:
            result = None
            retries = 0
            
            while retries <= self.max_retries_per_question:
                try:
                    # Attempt to process the question
                    response = llm_client.generate_response(
                        prompt=self._build_question_prompt(question)
                    )
                    
                    # Parse response
                    result = json.loads(response)
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    retries += 1
                    if retries <= self.max_retries_per_question:
                        self.logger.warning(f"Retrying question {question['id']} (attempt {retries})")
                    else:
                        # All retries exhausted, log failure and skip
                        self.logger.error(f"Question {question['id']} failed after {retries} attempts: {e}")
                        break
            
            results.append(result)
        
        return results
    
    def process_questions_with_detailed_report(self, questions: List[Dict], llm_client) -> Tuple[List[Optional[Dict]], Dict]:
        """
        Process questions and generate a detailed failure report.
        
        Args:
            questions: List of question dictionaries
            llm_client: LLM client for processing questions
            
        Returns:
            Tuple of (results, failure_report)
        """
        results = []
        failed_questions = []
        successful_count = 0
        
        for i, question in enumerate(questions):
            result = None
            try:
                response = llm_client.generate_response(
                    prompt=self._build_question_prompt(question)
                )
                result = json.loads(response)
                successful_count += 1
            except Exception as e:
                self.logger.error(f"Question {question['id']} failed: {e}")
                failed_questions.append({
                    'id': question['id'],
                    'text': question['text'],
                    'error': str(e),
                    'index': i
                })
            
            results.append(result)
        
        # Generate failure report
        failure_report = {
            'total_questions': len(questions),
            'successful_questions': successful_count,
            'failed_questions': failed_questions,
            'success_rate': successful_count / len(questions) if questions else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        return results, failure_report
    
    def process_questions_with_metadata(self, questions: List[Dict], llm_client) -> Tuple[List[Optional[Dict]], Dict]:
        """
        Process questions and collect metadata about the process.
        
        Args:
            questions: List of question dictionaries
            llm_client: LLM client for processing questions
            
        Returns:
            Tuple of (results, metadata)
        """
        results = []
        failed_count = 0
        
        for question in questions:
            result = None
            try:
                response = llm_client.generate_response(
                    prompt=self._build_question_prompt(question)
                )
                result = json.loads(response)
            except Exception as e:
                self.logger.error(f"Question {question['id']} failed: {e}")
                failed_count += 1
            
            results.append(result)
        
        # Generate metadata
        total_questions = len(questions)
        success_count = total_questions - failed_count
        completion_status = 'completed' if failed_count == 0 else 'partial' if success_count > 0 else 'failed'
        
        metadata = {
            'total_questions': total_questions,
            'success_count': success_count,
            'failed_count': failed_count,
            'success_rate': success_count / total_questions if total_questions > 0 else 0,
            'completion_status': completion_status,
            'timestamp': datetime.now().isoformat()
        }
        
        return results, metadata
    
    def process_questions_with_notifications(self, questions: List[Dict], llm_client) -> Tuple[List[Optional[Dict]], Dict]:
        """
        Process questions and generate user notifications for failures.
        
        Args:
            questions: List of question dictionaries
            llm_client: LLM client for processing questions
            
        Returns:
            Tuple of (results, notifications)
        """
        results = []
        failed_questions = []
        error_messages = []
        
        for question in questions:
            result = None
            try:
                response = llm_client.generate_response(
                    prompt=self._build_question_prompt(question)
                )
                result = json.loads(response)
            except Exception as e:
                self.logger.error(f"Question {question['id']} failed: {e}")
                failed_questions.append(question['id'])
                error_messages.append(str(e))
            
            results.append(result)
        
        # Generate notifications
        notifications = {
            'failed_questions': failed_questions,
            'error_messages': error_messages,
            'total_failed': len(failed_questions),
            'timestamp': datetime.now().isoformat()
        }
        
        return results, notifications
    
    def process_questions_with_statistics(self, questions: List[Dict], llm_client) -> Tuple[List[Optional[Dict]], Dict]:
        """
        Process questions and collect detailed statistics.
        
        Args:
            questions: List of question dictionaries
            llm_client: LLM client for processing questions
            
        Returns:
            Tuple of (results, statistics)
        """
        results = []
        failed_questions = []
        category_failures = {}
        
        for question in questions:
            result = None
            try:
                response = llm_client.generate_response(
                    prompt=self._build_question_prompt(question)
                )
                result = json.loads(response)
            except Exception as e:
                self.logger.error(f"Question {question['id']} failed: {e}")
                failed_questions.append(question['id'])
                
                # Track failures by category
                category = question.get('category', 'unknown')
                if category not in category_failures:
                    category_failures[category] = 0
                category_failures[category] += 1
            
            results.append(result)
        
        # Calculate statistics
        total_questions = len(questions)
        successful_questions = total_questions - len(failed_questions)
        success_rate = successful_questions / total_questions if total_questions > 0 else 0
        
        statistics = {
            'total_questions': total_questions,
            'successful_questions': successful_questions,
            'failed_questions': len(failed_questions),
            'success_rate': success_rate,
            'failure_rate': 1 - success_rate,
            'failed_categories': category_failures,
            'timestamp': datetime.now().isoformat()
        }
        
        return results, statistics
    
    def process_questions_with_fallback(self, questions: List[Dict], primary_client, fallback_client = None) -> List[Optional[Dict]]:
        """
        Process questions with fallback mechanism for failures.
        
        Args:
            questions: List of question dictionaries
            primary_client: Primary LLM client
            fallback_client: Fallback LLM client (optional)
            
        Returns:
            List of results (None for failed questions)
        """
        results = []
        
        for question in questions:
            result = None
            primary_failed = False
            
            # Try primary client
            try:
                response = primary_client.generate_response(
                    prompt=self._build_question_prompt(question)
                )
                result = json.loads(response)
            except Exception as e:
                self.logger.error(f"Primary client failed for question {question['id']}: {e}")
                primary_failed = True
            
            # Try fallback if primary failed and fallback is available
            if primary_failed and self.use_fallback and fallback_client:
                try:
                    response = fallback_client.generate_response(
                        prompt=self._build_question_prompt(question)
                    )
                    result = json.loads(response)
                    self.logger.info(f"Fallback client succeeded for question {question['id']}")
                except Exception as e:
                    self.logger.error(f"Fallback client also failed for question {question['id']}: {e}")
            
            results.append(result)
        
        return results
    
    def process_complete_assessment(self, questions: List[Dict], llm_client) -> Tuple[List[Optional[Dict]], Dict]:
        """
        Process a complete psychological assessment with comprehensive failure handling.
        
        Args:
            questions: List of question dictionaries
            llm_client: LLM client for processing questions
            
        Returns:
            Tuple of (results, summary)
        """
        results = []
        failed_responses = 0
        
        for question in questions:
            result = None
            try:
                response = llm_client.generate_response(
                    prompt=self._build_question_prompt(question)
                )
                result = json.loads(response)
            except Exception as e:
                self.logger.error(f"Question {question['id']} failed: {e}")
                failed_responses += 1
            
            results.append(result)
        
        # Generate summary
        total_questions = len(questions)
        successful_responses = total_questions - failed_responses
        completion_rate = successful_responses / total_questions if total_questions > 0 else 0
        assessment_status = 'completed' if failed_responses == 0 else 'completed_with_failures' if successful_responses > 0 else 'failed'
        
        summary = {
            'total_questions': total_questions,
            'successful_responses': successful_responses,
            'failed_responses': failed_responses,
            'completion_rate': completion_rate,
            'assessment_status': assessment_status,
            'timestamp': datetime.now().isoformat()
        }
        
        return results, summary
    
    def _build_question_prompt(self, question: Dict) -> str:
        """
        Build a prompt for processing a single question.
        
        Args:
            question: Question dictionary
            
        Returns:
            Formatted prompt string
        """
        # This is a simplified prompt builder
        # In a real implementation, this would be more sophisticated
        return f"Please answer the following question: {question['text']}"


# Example usage:
# handler = QuestionFailureHandler(max_retries_per_question=2, use_fallback=True)
# 
# questions = [
#     {"id": "q1", "text": "你经常感到精力充沛吗？", "type": "energy"},
#     {"id": "q2", "text": "你容易感到焦虑吗？", "type": "anxiety"}
# ]
# 
# # Process with skip mechanism
# results = handler.process_questions_with_skip(questions, llm_client)
# 
# # Process with detailed report
# results, report = handler.process_questions_with_detailed_report(questions, llm_client)