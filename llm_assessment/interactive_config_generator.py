#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interactive Configuration Generator for Psy2 Batch Testing
A user-friendly interface to generate batch test configurations using templates.
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Any
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the config template manager
from llm_assessment.config_templates import ConfigTemplateManager

# Ensure UTF-8 encoding for stdout/stdin on Windows
# if sys.platform.startswith('win'):
#     import io
#     sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
#     sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

# Load config.json
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")
try:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        app_config = json.load(f)
    TEST_FILES_CONFIG = app_config.get("test_files", {})
    # Create a mapping from file paths to config keys
    TEST_FILE_PATH_TO_KEY = {v: k for k, v in TEST_FILES_CONFIG.items()}
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading {CONFIG_FILE}: {e}")
    TEST_FILES_CONFIG = {}
    TEST_FILE_PATH_TO_KEY = {}

# --- Constants ---
# Use absolute path based on the script's location
LLM_ASSESSMENT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_FILES_DIR = os.path.join(LLM_ASSESSMENT_DIR, "test_files")
ROLES_DIR = os.path.join(LLM_ASSESSMENT_DIR, "roles")
RESULTS_DIR = os.path.join(LLM_ASSESSMENT_DIR, "results")

def get_available_files(directory: str, extension: str, language: str = "en", file_type: str = "test") -> List[str]:
    """Gets a list of files with a specific extension from a directory, filtered by language."""
    if not os.path.exists(directory):
        return []
    
    files = [f for f in os.listdir(directory) if f.endswith(extension)]
    
    # Filter by language
    if language == "en":
        # For English, include files with _en suffix
        if file_type == "role":
            files = [f for f in files if '_en' in f]
        else:
            files = [f for f in files if '_en' in f]
    elif language == "zh":
        # For Chinese, include files without _en suffix
        if file_type == "role":
            files = [f for f in files if '_en' not in f and f != "temp_role_en.txt"]
        else:
            files = [f for f in files if '_en' not in f]
    
    return files

def select_options(options: List[str], prompt: str, multi_select: bool = True) -> List[str]:
    """Generic function to prompt user to select one or more options from a list."""
    if not options:
        print(f"Warning: No options available for: {prompt}")
        return []

    print(f"\n--- {prompt} ---")
    for i, option in enumerate(options, 1):
        print(f"  {i:2d}. {option}")
    
    if multi_select:
        print("\n  A. All of the above")
        print("  N. None of the above")
        instruction = "Enter number(s) separated by commas, or A/N: "
    else:
        instruction = "Enter a single number: "

    while True:
        try:
            choice = input(instruction).strip().lower()
            if not choice:
                continue

            if multi_select:
                if choice == 'a':
                    return options
                if choice == 'n':
                    return []
                indices = [int(x.strip()) - 1 for x in choice.split(',')]
                if all(0 <= idx < len(options) for idx in indices):
                    return [options[idx] for idx in indices]
            else:
                index = int(choice) - 1
                if 0 <= index < len(options):
                    return [options[index]]
            
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter numbers only.")
        except EOFError:
            # Handle non-interactive environments
            print("\nNon-interactive mode: Selecting all options by default.")
            return options

def select_language() -> str:
    """Prompts user to select language."""
    print("\nSelect Language:")
    print("  1. English (en)")
    print("  2. Chinese (zh)")
    while True:
        try:
            lang_choice = int(input("Enter choice (1-2): ").strip())
            if lang_choice == 1:
                return "en"
            elif lang_choice == 2:
                return "zh"
            else:
                print("Please enter 1 or 2.")
        except ValueError:
            print("Please enter a valid number.")
        except EOFError:
            # Handle non-interactive environments
            print("\nNon-interactive mode: Using English by default.")
            return "en"

def select_template(manager: ConfigTemplateManager) -> str:
    """Prompts user to select a configuration template."""
    templates = manager.list_templates()
    
    print("\n--- Available Configuration Templates ---")
    for i, template in enumerate(templates, 1):
        print(f"  {i:2d}. {template['display_name']}")
        print(f"      {template['description']}")
        print(f"      Estimated tasks: {template['estimated_multiplier']} × (models × test files × roles)")
        if template.get("warning"):
            print(f"      ⚠️  {template['warning']}")
        print()
    
    while True:
        try:
            choice = int(input("Select a template (1-{}): ".format(len(templates))).strip())
            if 1 <= choice <= len(templates):
                return templates[choice-1]["name"]
            else:
                print("Please enter a valid option number.")
        except ValueError:
            print("Please enter a valid number.")
        except EOFError:
            # Handle non-interactive environments
            print("\nNon-interactive mode: Using 'baseline' template by default.")
            return "baseline"

def select_models() -> List[str]:
    """Prompts user to select models."""
    # For now, we'll provide a list of common models
    # In a more advanced version, we could integrate with Ollama to get available models
    common_models = [
        "gemma3:latest",
        "llama3.2:latest",
        "qwen3:latest",
        "phi3:latest",
        "mistral:latest",
        "deepseek-r1:8b"
    ]
    
    print("\n--- Model Selection ---")
    print("Select from common models:")

    selected_common = select_options(common_models, "Select Common Models", multi_select=True)

    # 直接返回选择的模型，不进行任何自定义模型询问
    if not selected_common:
        print("No models selected. Using default model.")
        return ["gemma3:latest"]

    return selected_common

def generate_config_non_interactive(template_name: str, models: List[str], test_files: List[str], 
                                  roles: List[str], output_file: str = None) -> Dict[str, Any]:
    """Generate configuration in non-interactive mode."""
    manager = ConfigTemplateManager()
    
    # Validate template
    if not manager.get_template(template_name):
        available_templates = [t["name"] for t in manager.list_templates()]
        raise ValueError(f"Template '{template_name}' not found. Available templates: {available_templates}")
    
    # Generate the configuration
    config = manager.generate_config(template_name, models, test_files, roles)
    
    # Save configuration
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"batch_config_{template_name}_{timestamp}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully created '{output_file}'.")
    print(f"Configuration contains {len(config['test_suites'][0]['tasks'])} tasks.")
    
    return config

def main():
    """Main function to drive the interactive configuration generation."""
    parser = argparse.ArgumentParser(description="Generate batch test configurations for Psy2")
    parser.add_argument("--non-interactive", action="store_true", 
                        help="Run in non-interactive mode")
    parser.add_argument("--template", type=str, 
                        help="Template name for non-interactive mode")
    parser.add_argument("--models", type=str, nargs="+", 
                        help="Model names for non-interactive mode")
    parser.add_argument("--test-files", type=str, nargs="+", 
                        help="Test files for non-interactive mode")
    parser.add_argument("--roles", type=str, nargs="+", 
                        help="Roles for non-interactive mode")
    parser.add_argument("--output", type=str, 
                        help="Output file name")
    
    args = parser.parse_args()
    
    # Non-interactive mode
    if args.non_interactive:
        if not all([args.template, args.models, args.test_files, args.roles]):
            print("Non-interactive mode requires --template, --models, --test-files, and --roles")
            return
        
        try:
            generate_config_non_interactive(
                args.template, args.models, args.test_files, args.roles, args.output
            )
        except Exception as e:
            print(f"Error generating configuration: {e}")
            return
        return
    
    # Interactive mode
    print("==================================================")
    print("=== Interactive Psy2 Configuration Generator ===")
    print("==================================================")
    
    # Initialize the template manager
    manager = ConfigTemplateManager()
    
    # Select language
    language = select_language()
    
    # Select template
    template_name = select_template(manager)
    template = manager.get_template(template_name)
    
    # Select models
    selected_models = select_models()
    
    # Get available tests - fix for directory structure
    available_tests = []

    # Based on selected language, look in appropriate subdirectory
    if language == "en":
        subdir_path = os.path.join(TEST_FILES_DIR, "English")
        if os.path.exists(subdir_path):
            available_tests = [os.path.join("English", f) for f in os.listdir(subdir_path) if f.endswith('.json')]
    elif language == "zh":
        subdir_path = os.path.join(TEST_FILES_DIR, "中文版")
        if os.path.exists(subdir_path):
            available_tests = [os.path.join("中文版", f) for f in os.listdir(subdir_path) if f.endswith('.json')]

    # If no tests found based on language, try both directories
    if not available_tests:
        for subdir in ['中文版', 'English']:
            subdir_path = os.path.join(TEST_FILES_DIR, subdir)
            if os.path.exists(subdir_path):
                subdir_tests = [os.path.join(subdir, f) for f in os.listdir(subdir_path) if f.endswith('.json')]
                available_tests.extend(subdir_tests)

    if available_tests:
        # Show a debug message to confirm we found files
        print(f"Found {len(available_tests)} test files")

        # For display in select_options, just use the filename without the subdirectory prefix
        display_tests = [os.path.basename(test) for test in available_tests]

        selected_tests = select_options(display_tests, "Select Psychological Tests")

        # Map back to the full paths for actual use
        selected_tests_full_path = []
        for sel_test in selected_tests:
            # Find the original full path for the selected test
            for full_path_test in available_tests:
                if os.path.basename(full_path_test) == sel_test:
                    selected_tests_full_path.append(full_path_test)
                    break
    else:
        print("No tests found in test file directories.")
        print("No tests selected. Exiting.")
        return
    
    # Get available roles based on language
    available_roles = ["default"] + get_available_files(ROLES_DIR, ".txt", language, "role")
    selected_roles = select_options(available_roles, "Select Roles to Apply")
    # Handle case where no roles are selected - use default
    if not selected_roles:
        print("No roles selected. Using default role.")
        selected_roles = ["default"]
    
    # Calculate estimated task count
    estimated_tasks = manager.calculate_task_count(template_name, selected_models, selected_tests_full_path, selected_roles)
    print(f"\nEstimated number of tasks to be generated: {estimated_tasks}")

    if estimated_tasks > 1000:
        try:
            confirm = input("This will generate a large number of tasks. Continue? (y/N): ").strip().lower()
            if confirm != 'y':
                print("Configuration generation cancelled.")
                return
        except EOFError:
            # Handle non-interactive environments
            print("\nNon-interactive mode: Continuing with large task generation.")

    print("\n--- Generating Configuration ---")

    try:
        # Generate the configuration
        config = manager.generate_config(template_name, selected_models, selected_tests_full_path, selected_roles)
        
        # Save configuration
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        config_filename = f"batch_config_{template_name}_{timestamp}.json"
        
        with open(config_filename, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully created '{config_filename}'.")
        print(f"Configuration contains {len(config['test_suites'][0]['tasks'])} tasks.")
        
        # Ask if user wants to run the batch test
        try:
            run_choice = input("\nDo you want to run the batch test now? (y/N): ").strip().lower()
            if run_choice == 'y':
                print("To run the batch test, execute:")
                print(f"  python llm_assessment/run_batch_suite.py {config_filename}")
        except EOFError:
            # Handle non-interactive environments
            print("\nNon-interactive mode: Configuration generated successfully.")
        
    except Exception as e:
        print(f"Error generating configuration: {e}")
        return

from python_utf8_config import ensure_utf8

if __name__ == "__main__":
    ensure_utf8()
    main()