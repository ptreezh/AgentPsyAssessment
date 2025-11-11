#!/usr/bin/env python3
"""
Base classes and interfaces for unified assessment skills system.

This module provides the abstract base classes and common infrastructure
that all assessment skills will inherit from and use.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import os
from pathlib import Path

from .config_validator import ConfigurationValidator
from .assessment_detector import AssessmentTypeDetector, DetectionResult


class AssessmentType(Enum):
    """Supported assessment types."""
    BIG_FIVE_PERSONALITY = "big_five_personality"
    CITIZENSHIP_KNOWLEDGE = "citizenship_knowledge"
    FINANCIAL_PROFESSIONAL = "financial_professional"
    LEGAL_KNOWLEDGE = "legal_knowledge"
    MOTIVATION_PSYCHOLOGY = "motivation_psychology"
    POLITICAL_LITERACY = "political_literacy"


@dataclass
class AssessmentContext:
    """Context information for assessment operations."""
    assessment_type: AssessmentType
    config: Dict[str, Any]
    persona: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AssessmentResult:
    """Result of an assessment operation."""
    success: bool
    assessment_type: AssessmentType
    data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QuestionResponse:
    """Response to a single assessment question."""
    question_id: str
    response: Any
    confidence: float = 0.0
    reasoning: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    """Result of evaluating a response."""
    question_id: str
    score: float
    dimension_scores: Dict[str, float] = field(default_factory=dict)
    feedback: Optional[str] = None
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAssessmentSkill(ABC):
    """Abstract base class for all assessment skills."""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the assessment skill.

        Args:
            config_dir: Directory containing configuration files
        """
        self.config_validator = ConfigurationValidator(config_dir)
        self.configs = self.config_validator.load_all_configs()
        self.detector = AssessmentTypeDetector(self.configs)
        self._sessions: Dict[str, Dict[str, Any]] = {}

    @abstractmethod
    def get_skill_name(self) -> str:
        """Get the name of this skill."""
        pass

    @abstractmethod
    def get_supported_assessment_types(self) -> List[AssessmentType]:
        """Get list of supported assessment types."""
        pass

    @abstractmethod
    def process_request(self, request_data: Dict[str, Any]) -> AssessmentResult:
        """
        Process an assessment request.

        Args:
            request_data: Request data containing assessment details

        Returns:
            AssessmentResult with the operation result
        """
        pass

    def detect_assessment_type(self, content: Dict[str, Any],
                              filename: str = "") -> DetectionResult:
        """
        Detect the assessment type from content.

        Args:
            content: Assessment content
            filename: Optional filename for context

        Returns:
            DetectionResult with detected type and confidence
        """
        return self.detector.detect_from_content(content, filename)

    def load_config_for_type(self, assessment_type: Union[str, AssessmentType]) -> Optional[Dict[str, Any]]:
        """
        Load configuration for a specific assessment type.

        Args:
            assessment_type: The assessment type to load config for

        Returns:
            Configuration dictionary or None if not found
        """
        type_str = assessment_type.value if isinstance(assessment_type, AssessmentType) else assessment_type
        return self.configs.get(type_str)

    def create_context(self, assessment_type: Union[str, AssessmentType],
                      persona: Optional[str] = None,
                      parameters: Optional[Dict[str, Any]] = None,
                      **kwargs) -> AssessmentContext:
        """
        Create an assessment context.

        Args:
            assessment_type: The assessment type
            persona: Optional persona for role-playing
            parameters: Optional parameters
            **kwargs: Additional context data

        Returns:
            AssessmentContext instance
        """
        type_str = assessment_type.value if isinstance(assessment_type, AssessmentType) else assessment_type
        config = self.load_config_for_type(type_str)

        if not config:
            raise ValueError(f"No configuration found for assessment type: {type_str}")

        return AssessmentContext(
            assessment_type=AssessmentType(type_str),
            config=config,
            persona=persona,
            parameters=parameters or {},
            **kwargs
        )

    def validate_context(self, context: AssessmentContext) -> Tuple[bool, List[str]]:
        """
        Validate an assessment context.

        Args:
            context: The context to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check assessment type
        if not isinstance(context.assessment_type, AssessmentType):
            errors.append("assessment_type must be an AssessmentType enum")

        # Check configuration
        if not context.config:
            errors.append("Configuration is required")

        # Validate configuration
        if context.config:
            is_valid, config_errors = self.config_validator.validate_config(context.config)
            if not is_valid:
                errors.extend(config_errors)

        return len(errors) == 0, errors

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session data or None if not found
        """
        return self._sessions.get(session_id)

    def create_session(self, context: AssessmentContext) -> str:
        """
        Create a new assessment session.

        Args:
            context: Assessment context

        Returns:
            Session ID
        """
        import uuid
        session_id = str(uuid.uuid4())

        self._sessions[session_id] = {
            "context": context,
            "created_at": self._get_timestamp(),
            "data": {},
            "metadata": {}
        }

        return session_id

    def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Update session data.

        Args:
            session_id: Session identifier
            data: Data to update

        Returns:
            True if successful, False if session not found
        """
        if session_id not in self._sessions:
            return False

        self._sessions[session_id]["data"].update(data)
        self._sessions[session_id]["updated_at"] = self._get_timestamp()
        return True

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session identifier

        Returns:
            True if successful, False if session not found
        """
        if session_id not in self._sessions:
            return False

        del self._sessions[session_id]
        return True

    def list_sessions(self) -> List[str]:
        """Get list of active session IDs."""
        return list(self._sessions.keys())

    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().isoformat()

    def _format_error_result(self, assessment_type: AssessmentType,
                           error_message: str, **kwargs) -> AssessmentResult:
        """
        Create an error result.

        Args:
            assessment_type: The assessment type
            error_message: Error message
            **kwargs: Additional metadata

        Returns:
            AssessmentResult with error information
        """
        return AssessmentResult(
            success=False,
            assessment_type=assessment_type,
            error_message=error_message,
            metadata=kwargs
        )

    def _format_success_result(self, assessment_type: AssessmentType,
                             data: Dict[str, Any], confidence: float = 0.0,
                             **kwargs) -> AssessmentResult:
        """
        Create a success result.

        Args:
            assessment_type: The assessment type
            data: Result data
            confidence: Confidence score
            **kwargs: Additional metadata

        Returns:
            AssessmentResult with success information
        """
        return AssessmentResult(
            success=True,
            assessment_type=assessment_type,
            data=data,
            confidence=confidence,
            metadata=kwargs
        )


class BaseQuestionnaireSkill(BaseAssessmentSkill):
    """Base class for questionnaire responder skills."""

    @abstractmethod
    def generate_responses(self, context: AssessmentContext,
                          questions: List[Dict[str, Any]]) -> List[QuestionResponse]:
        """
        Generate responses to questionnaire questions.

        Args:
            context: Assessment context
            questions: List of questions to respond to

        Returns:
            List of QuestionResponse objects
        """
        pass

    @abstractmethod
    def validate_response(self, context: AssessmentContext,
                         question: Dict[str, Any],
                         response: Any) -> Tuple[bool, List[str]]:
        """
        Validate a response against question requirements.

        Args:
            context: Assessment context
            question: Question data
            response: Response to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        pass


class BaseAnalyzerSkill(BaseAssessmentSkill):
    """Base class for psychological analyzer skills."""

    @abstractmethod
    def start_evaluation_session(self, context: AssessmentContext,
                               total_questions: int) -> str:
        """
        Start an evaluation session.

        Args:
            context: Assessment context
            total_questions: Total number of questions to evaluate

        Returns:
            Session ID
        """
        pass

    @abstractmethod
    def evaluate_response(self, session_id: str,
                         question: Dict[str, Any],
                         response: Any) -> EvaluationResult:
        """
        Evaluate a single response.

        Args:
            session_id: Session identifier
            question: Question data
            response: Response to evaluate

        Returns:
            EvaluationResult with scores and feedback
        """
        pass

    @abstractmethod
    def complete_evaluation(self, session_id: str) -> AssessmentResult:
        """
        Complete an evaluation session and generate final results.

        Args:
            session_id: Session identifier

        Returns:
            AssessmentResult with complete evaluation
        """
        pass


class BaseReportGeneratorSkill(BaseAssessmentSkill):
    """Base class for evaluation report generator skills."""

    @abstractmethod
    def generate_report(self, context: AssessmentContext,
                       evaluation_data: Dict[str, Any],
                       output_path: Optional[str] = None,
                       template_style: Optional[str] = None) -> str:
        """
        Generate an evaluation report.

        Args:
            context: Assessment context
            evaluation_data: Data from evaluation
            output_path: Optional output file path
            template_style: Optional template style

        Returns:
            Path to generated report
        """
        pass

    @abstractmethod
    def get_available_templates(self, assessment_type: AssessmentType) -> List[str]:
        """
        Get available report templates for an assessment type.

        Args:
            assessment_type: The assessment type

        Returns:
            List of template names
        """
        pass


class SkillFactory:
    """Factory for creating assessment skill instances."""

    _skills: Dict[str, type] = {}

    @classmethod
    def register_skill(cls, name: str, skill_class: type):
        """
        Register a skill class.

        Args:
            name: Skill name
            skill_class: Skill class (must inherit from BaseAssessmentSkill)
        """
        if not issubclass(skill_class, BaseAssessmentSkill):
            raise ValueError(f"Skill class must inherit from BaseAssessmentSkill")

        cls._skills[name] = skill_class

    @classmethod
    def create_skill(cls, name: str, **kwargs) -> BaseAssessmentSkill:
        """
        Create a skill instance.

        Args:
            name: Skill name
            **kwargs: Additional arguments for skill constructor

        Returns:
            Skill instance
        """
        if name not in cls._skills:
            raise ValueError(f"Unknown skill: {name}")

        return cls._skills[name](**kwargs)

    @classmethod
    def list_skills(cls) -> List[str]:
        """Get list of registered skill names."""
        return list(cls._skills.keys())

    @classmethod
    def get_skill_info(cls, name: str) -> Dict[str, Any]:
        """
        Get information about a skill.

        Args:
            name: Skill name

        Returns:
            Skill information dictionary
        """
        if name not in cls._skills:
            raise ValueError(f"Unknown skill: {name}")

        skill_class = cls._skills[name]

        # Create temporary instance to get info
        try:
            temp_instance = skill_class()
            return {
                "name": name,
                "class": skill_class.__name__,
                "skill_name": temp_instance.get_skill_name(),
                "supported_types": [t.value for t in temp_instance.get_supported_assessment_types()],
                "description": temp_instance.__class__.__doc__ or "No description available"
            }
        except Exception as e:
            return {
                "name": name,
                "class": skill_class.__name__,
                "error": str(e)
            }


def register_skill(skill_name: str):
    """
    Decorator for registering skills.

    Args:
        skill_name: Name to register the skill under
    """
    def decorator(cls):
        SkillFactory.register_skill(skill_name, cls)
        return cls
    return decorator