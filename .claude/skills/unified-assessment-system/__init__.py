"""
Unified Assessment Skills System

A comprehensive framework for psychological and professional assessment
that supports multiple assessment types through a unified architecture.

Supported assessment types:
- Big Five Personality Assessment (大五人格职业化测评)
- Citizenship Knowledge Assessment (公民知识测评)
- Financial Professional Assessment (金融专业测评)
- Legal Knowledge Assessment (法律知识测评)
- Motivation Psychology Assessment (动机心理学测评)
- Political Literacy Assessment (政治素养测评)

Core components:
- Configuration management and validation
- Automatic assessment type detection
- Base classes for skills (Questionnaire, Analyzer, Report Generator)
- Skill factory for dynamic skill creation
"""

from .skill_base import (
    AssessmentType,
    AssessmentContext,
    AssessmentResult,
    QuestionResponse,
    EvaluationResult,
    BaseAssessmentSkill,
    BaseQuestionnaireSkill,
    BaseAnalyzerSkill,
    BaseReportGeneratorSkill,
    SkillFactory,
    register_skill
)

from .config_validator import ConfigurationValidator
from .assessment_detector import AssessmentTypeDetector, DetectionResult

__version__ = "1.0.0"
__author__ = "Unified Assessment Team"

__all__ = [
    # Core enums and data classes
    "AssessmentType",
    "AssessmentContext",
    "AssessmentResult",
    "QuestionResponse",
    "EvaluationResult",
    "DetectionResult",

    # Base classes
    "BaseAssessmentSkill",
    "BaseQuestionnaireSkill",
    "BaseAnalyzerSkill",
    "BaseReportGeneratorSkill",

    # Utility classes
    "ConfigurationValidator",
    "AssessmentTypeDetector",
    "SkillFactory",
    "register_skill",

    # Constants
    "__version__",
    "__author__"
]

# Package metadata
PACKAGE_INFO = {
    "name": "unified-assessment-system",
    "version": "1.0.0",
    "description": "Unified framework for psychological and professional assessment",
    "supported_assessment_types": [
        "big_five_personality",
        "citizenship_knowledge",
        "financial_professional",
        "legal_knowledge",
        "motivation_psychology",
        "political_literacy"
    ],
    "skill_types": [
        "questionnaire-responder",
        "psychological-analyzer",
        "evaluation-report-generator"
    ]
}


def get_package_info():
    """Get package information."""
    return PACKAGE_INFO


def get_supported_assessment_types():
    """Get list of supported assessment types."""
    return [t.value for t in AssessmentType]


def is_assessment_type_supported(assessment_type: str) -> bool:
    """Check if an assessment type is supported."""
    try:
        AssessmentType(assessment_type)
        return True
    except ValueError:
        return False