#!/usr/bin/env python3
"""
Legacy Assessment Runner (Archived)
This file contains the archived code for the '--mode assessment' functionality
that was previously part of `shared_analysis/interactive_analysis.py`.

As of 2025-08-23, this functionality has been removed from the main interactive
analysis script and the dedicated `llm_assessment` module should be used instead.

Files affected by this archival:
- `shared_analysis/interactive_analysis.py` (Removed assessment mode code)
- This file (`shared_analysis/archived_assessment_runner.py`) created to store the legacy code.

Reason for archival:
- Clear separation of concerns: `shared_analysis` should focus on analyzing results,
  not running new assessments.
- Redundancy: The `llm_assessment` module already provides comprehensive assessment
  running capabilities.
"""

# --- LEGACY CODE IMPORTS (for reference only) ---
# import sys
# import os
# import json
# import argparse
# from typing import List, Dict, Any
# from pathlib import Path
# from datetime import datetime

# from llm_assessment.services.llm_client import LLMClient
# from llm_assessment.services.model_manager import ModelManager
# from llm_assessment.run_assessment_unified import (
#     test_model_connectivity,
#     load_test_file,
#     load_role_prompt,
#     run_assessment,
#     save_results,
#     generate_filename,
#     TEST_ABBREVIATIONS
# )

# --- LEGACY CONSTANTS (for reference only) ---
# ROLES_DIR = "llm_assessment/roles"
# TESTS_DIR = "llm_assessment/test_files"
# RESULTS_DIR = "results"
# AVAILABLE_MODELS_FILE = "available_models.txt"

# --- LEGACY FUNCTIONS (for reference only) ---

# def load_available_models() -> Dict[str, Dict[str, str]]:
#     ...

# def save_available_models(models: Dict[str, Dict[str, str]]) -> None:
#     ...

# def get_available_tests() -> List[str]:
#     ...

# def get_available_roles() -> List[str]:
#     ...

# def select_multiple_options(options: List[str], prompt: str) -> List[str]:
#     ...

# def select_single_option(options: List[str], prompt: str) -> str:
#     ...

# def run_tests(client, selected_models, selected_tests, selected_roles):
#     ...

# def run_interactive_assessment():
#     """Interactive assessment runner using robust assessment"""
#     ...