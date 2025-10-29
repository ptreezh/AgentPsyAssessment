"""
Analysis package for AgentPsyAssessment
This package contains modules for analyzing psychological assessment results.
"""

__version__ = "1.0.0"
__author__ = "Zhang"

# Import key functions for easier access
from .analyze_results import run_analysis

__all__ = [
    "run_analysis",
]