#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interactive Batch Test Suite Runner for Persona-Analyzer
A user-friendly interface to configure and execute batch personality assessments.
"""

import os
import json
import subprocess
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure UTF-8 encoding for stdout/stderr on Windows
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

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
LLM_ASSESSMENT_DIR = "."
TEST_FILES_DIR = os.path.join(LLM_ASSESSMENT_DIR, "test_files")
ROLES_DIR = os.path.join(LLM_ASSESSMENT_DIR, "roles")
RESULTS_DIR = os.path.join(LLM_ASSESSMENT_DIR, "results")

# --- Default Parameters ---
DEFAULT_PARAMS = {
    "emotional_stress_level": None,
    "cognitive_trap_type": None,
    "tmpr": 0.7,
    "context_length_mode": "auto",
    "role": "default"
}

# --- Helper Functions ---

def load_evaluator_config_from_env(env_file_path=".env"):
    """Loads evaluator-specific configurations from a .env file."""
    config = {}
    if not os.path.exists(env_file_path):
        print(f"Warning: .env file not found at {env_file_path}")
        return config
        
    with open(env_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key] = value.strip()
                    
    return config

def get_available_evaluators(config):
    """Determines which evaluators are available based on the loaded config."""
    available_evaluators = []
    
    # Map of evaluator names to their required API key environment variable names
    evaluator_api_keys = {
        "gpt": ["OPENAI_API_KEY"],
        "claude": ["ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY"], # Support both old and new key names
        "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"], # Support both old and new key names
        "deepseek": ["DEEPSEEK_API_KEY", "MODELSCOPE_API_KEY"], # Support both old and new key names
        "glm": ["GLM_API_KEY"]
    }
    
    for evaluator, possible_keys in evaluator_api_keys.items():
        # Check if any of the possible API keys are set and not empty
        for key in possible_keys:
            if config.get(key, "").strip():
                available_evaluators.append(evaluator)
                break # Found one, no need to check others for this evaluator
                
    return available_evaluators

def get_ollama_models():
    """Gets a list of available Ollama models, excluding embedding models."""
    print("Fetching available Ollama models...")
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True, encoding='utf-8')
        lines = result.stdout.strip().split('\n')
        models = []
        for line in lines[1:]:
            model_name = line.split()[0]
            if "embed" not in model_name.lower():
                models.append(model_name)
        return models
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: 'ollama list' command failed or Ollama is not installed.")
        print("Please ensure Ollama is running and accessible.")
        return []

def get_available_files(directory, extension, language="en", file_type="test"):
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

def select_options(options, prompt, multi_select=True):
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

# --- NEW: Interactive Stress Testing Parameter Selection ---
def select_stress_testing_parameters():
    """Prompts user to select stress testing parameters."""
    print("\n--- Advanced Stress Testing Parameters ---")
    
    # Language selection
    print("\nSelect Language:")
    print("  1. English (en)")
    print("  2. Chinese (zh)")
    while True:
        try:
            lang_choice = int(input("Enter choice (1-2): ").strip())
            if lang_choice == 1:
                language = "en"
                break
            elif lang_choice == 2:
                language = "zh"
                break
            else:
                print("Please enter 1 or 2.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Emotional stress level selection
    emotional_stress_levels = list(range(0, 5))  # 0-4
    print("\nSelect Emotional Stress Levels (0=None):")
    for i, level in enumerate(emotional_stress_levels):
        level_desc = ["None", "Low", "Medium", "High", "Extreme"][level]
        print(f"  {i}. {level} ({level_desc})")
    
    selected_emotional_levels = select_options(
        [str(i) for i in emotional_stress_levels], 
        "Select Emotional Stress Levels", 
        multi_select=True
    )
    selected_emotional_levels = [int(i) for i in selected_emotional_levels]
    
    # Cognitive trap type selection
    cognitive_trap_types = {
        'p': 'Paradox (p)',
        'c': 'Circularity (c)',
        's': 'Semantic Fallacy (s)',
        'r': 'Procedural (r)'
    }
    print("\nSelect Cognitive Trap Types:")
    for key, desc in cognitive_trap_types.items():
        print(f"  {key}. {desc}")
    
    selected_cognitive_traps = select_options(
        list(cognitive_trap_types.keys()),
        "Select Cognitive Trap Types",
        multi_select=True
    )
    
    # Temperature selection (0-5)
    temperature_options = [None, 0.0, 0.3, 0.8, 1.3, 1.8]
    temperature_descriptions = [
        "Default Temperature (Model Default)",
        "0 (Deterministic)",
        "0.3 (Low Creativity)", 
        "0.8 (Medium Creativity)",
        "1.3 (High Creativity)",
        "1.8 (Very High Creativity)"
    ]
    print("\nSelect Temperature Settings:")
    for i, (temp, desc) in enumerate(zip(temperature_options, temperature_descriptions)):
        print(f"  {i}. {desc}")
    
    selected_temperatures = select_options(
        [str(i) for i in range(len(temperature_options))],
        "Select Temperature Settings",
        multi_select=True
    )
    selected_temperatures = [temperature_options[int(i)] for i in selected_temperatures]
    
    # Context length mode selection
    print("\nSelect Context Length Mode:")
    context_length_modes = ['none', 'auto', 'static', 'dynamic']
    context_length_mode_descriptions = [
        "None (No context injection)",
        "Auto (Detect model capabilities)",
        "Static (Fixed length)",
        "Dynamic (Percentage-based)"
    ]
    for i, (mode, desc) in enumerate(zip(context_length_modes, context_length_mode_descriptions)):
        print(f"  {i}. {desc}")
    
    while True:
        try:
            mode_choice = input("Please select context length mode (0-2): ").strip()
            mode_index = int(mode_choice)
            if 0 <= mode_index < len(context_length_modes):
                context_length_mode = context_length_modes[mode_index]
                break
            else:
                print("Please enter a valid option number (0-2).")
        except ValueError:
            print("Please enter a valid number.")
    
    # Context length parameters based on mode
    static_context_length = 0
    dynamic_context_ratio = '1/2'
    
    if context_length_mode == 'static':
        print("\nSelect Static Context Length:")
        static_context_options = [0, 1, 2, 4, 8, 16, 32, 64]
        static_context_descriptions = [
            "0K (No context)",
            "1K Context",
            "2K Context",
            "4K Context",
            "8K Context",
            "16K Context",
            "32K Context",
            "64K Context"
        ]
        for i, (length, desc) in enumerate(zip(static_context_options, static_context_descriptions)):
            print(f"  {i}. {desc}")
        
        while True:
            try:
                static_choice = input("Please select static context length (0-7): ").strip()
                static_index = int(static_choice)
                if 0 <= static_index < len(static_context_options):
                    static_context_length = static_context_options[static_index]
                    break
                else:
                    print("Please enter a valid option number (0-7).")
            except ValueError:
                print("Please enter a valid number.")
    
    elif context_length_mode == 'dynamic':
        print("\nSelect Dynamic Context Length Ratio:")
        dynamic_context_options = ['1/4', '1/2', '3/4', '9/10']
        dynamic_context_descriptions = [
            "1/4 of Model Max Context",
            "1/2 of Model Max Context",
            "3/4 of Model Max Context",
            "9/10 of Model Max Context"
        ]
        for i, (ratio, desc) in enumerate(zip(dynamic_context_options, dynamic_context_descriptions)):
            print(f"  {i}. {desc}")
        
        while True:
            try:
                dynamic_choice = input("Please select dynamic context length ratio (0-3): ").strip()
                dynamic_index = int(dynamic_choice)
                if 0 <= dynamic_index < len(dynamic_context_options):
                    dynamic_context_ratio = dynamic_context_options[dynamic_index]
                    break
                else:
                    print("Please enter a valid option number (0-3).")
            except ValueError:
                print("Please enter a valid number.")
    
    return {
        'language': language,
        'emotional_stress_levels': selected_emotional_levels,
        'cognitive_trap_types': selected_cognitive_traps,
        'temperatures': selected_temperatures,
        'context_length_mode': context_length_mode,
        'static_context_length': static_context_length,
        'dynamic_context_ratio': dynamic_context_ratio
    }
# --- END NEW ---

# --- Main Script Logic ---

def main():
    """Main function to drive the interactive batch configuration and execution."""
    print("==================================================")
    print("=== Interactive Psy2 Batch Test Suite Runner ===")
    print("==================================================")

    debug_choice = input("Enable debug mode for verbose output? (y/N): ").strip().lower()
    debug_mode = debug_choice == 'y'
    if debug_mode:
        print("*** DEBUG MODE ENABLED ***")

    # Get available models
    ollama_models = get_ollama_models()

    if not ollama_models:
        sys.exit(1)
    selected_models = select_options(ollama_models, "Select Models to Test")
    if not selected_models:
        print("No models selected. Exiting.")
        sys.exit(0)

    # --- UPDATED: Select stress testing parameters including language ---
    stress_params = select_stress_testing_parameters()
    language = stress_params['language']
    # --- END UPDATED ---

    # Get available tests based on language
    available_tests = get_available_files(TEST_FILES_DIR, ".json", language, "test")
    selected_tests = select_options(available_tests, "Select Psychological Tests")
    if not selected_tests:
        print("No tests selected. Exiting.")
        sys.exit(0)

    # Get available roles based on language
    available_roles = ["default"] + get_available_files(ROLES_DIR, ".txt", language, "role")
    selected_roles = select_options(available_roles, "Select Roles to Apply")
    # Handle case where no roles are selected - use default
    if not selected_roles:
        print("No roles selected. Using default role.")
        selected_roles = ["default"]

    print("\n--- Generating batch_config.json ---")
    
    config_models = []
    for model_path in selected_models:
        alias = model_path.replace("/", "_").replace(":", "-")
        config_models.append({"name": alias, "path": model_path})

    tasks = []
    for test in selected_tests:
        for role in selected_roles:
            # --- UPDATED: Generate tasks with all combinations of stress parameters ---
            # Handle case where no stress parameters are selected
            emotional_levels = stress_params['emotional_stress_levels'] if stress_params['emotional_stress_levels'] else [None]
            cognitive_traps = stress_params['cognitive_trap_types'] if stress_params['cognitive_trap_types'] else [None]
            temperatures = stress_params['temperatures'] if stress_params['temperatures'] else [0.7]
            
            for emotional_level in emotional_levels:
                for cognitive_trap in cognitive_traps:
                    for temperature in temperatures:
                        # Create a descriptive task name
                        stress_info = "baseline"  # Default to baseline
                        if emotional_level is not None:
                            stress_info = f"esL{emotional_level}"
                        if cognitive_trap:
                            stress_info += f"_ct{cognitive_trap}"
                        if temperature is not None and temperature != 0.7:
                            stress_info += f"_tmp{temperature}"
                        if stress_params['context_length_mode'] != 'none':
                            stress_info += f"_cl{stress_params['context_length_mode']}"
                        
                        # Ensure role is a string
                        role_str = str(role) if role else "default"
                        if role_str == "default" and stress_info == "baseline":
                            task_name = f"{os.path.splitext(test)[0]}_baseline"
                        else:
                            task_name = f"{os.path.splitext(test)[0]}_{role_str.replace('.txt','')}_{stress_info}"
                        
                        # 修复：直接使用测试文件名，而不是完整路径
                        # 如果test是配置文件中的路径，则使用对应的键名
                        if test in TEST_FILE_PATH_TO_KEY:
                            test_file_key = TEST_FILE_PATH_TO_KEY[test]
                        else:
                            test_file_key = test
                        
                        task = {
                            "task_name": task_name,
                            "type": "questionnaire",
                            "test_file": test_file_key,  # 修复：只使用文件名或配置键名，不包含路径
                            "emotional_stress_level": emotional_level,
                            "tmpr": temperature
                        }
                        
                        # Only add context length parameters if context injection is enabled
                        if stress_params['context_length_mode'] != 'none':
                            task["context_length_mode"] = stress_params['context_length_mode']
                            task["context_length_static"] = stress_params['static_context_length']
                            task["context_length_dynamic"] = stress_params['dynamic_context_ratio']
                        
                        if cognitive_trap:
                            task["cognitive_trap_type"] = cognitive_trap
                        if role != "default":
                            # Use language-specific role directory
                            role_file_path = role  # 修复：只使用文件名，不包含路径
                            task["role_file"] = role_file_path
                        tasks.append(task)
            # --- END UPDATED ---

    # Ensure we have at least a baseline task
    if not tasks:
        for test in selected_tests:
            # 如果test是配置文件中的路径，则使用对应的键名
            if test in TEST_FILE_PATH_TO_KEY:
                test_file_key = TEST_FILE_PATH_TO_KEY[test]
            else:
                test_file_key = test
            
            task = {
                "task_name": f"{os.path.splitext(test)[0]}_baseline",
                "type": "questionnaire",
                "test_file": test_file_key,
                "emotional_stress_level": None,
                "tmpr": 0.7
            }
            tasks.append(task)

    batch_config = {
        "models": config_models,
        "test_suites": [
            {
                "suite_name": f"Interactive_Suite_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "models_to_run": [m["name"] for m in config_models],
                "tasks": tasks
            }
        ]
    }

    try:
        with open("batch_config.json", "w", encoding="utf-8") as f:
            json.dump(batch_config, f, indent=2)
        print("Successfully created 'batch_config.json'.")
    except IOError as e:
        print(f"Error writing config file: {e}")
        sys.exit(1)

    # --- NEW: Ask user if they want automatic analysis ---
    auto_analyze_choice = input("测试完成后，是否自动运行分析流程？ (y/N): ").strip().lower()
    auto_analyze = auto_analyze_choice == 'y'
    if auto_analyze:
        print("*** 自动分析模式已启用。 ***")
    # --- END NEW ---

    print("\n--------------------------------------------------")
    print("Configuration generated.")
    action = input("Press Enter to start the batch test suite, or enter 'g' to generate config only and exit: ").strip().lower()

    if action == 'q' or action == 'g':
        if action == 'g':
            print("Configuration file 'batch_config.json' has been generated. Exiting.")
        else:
            print("Execution cancelled by user.")
        sys.exit(0)

    print("Executing 'llm_assessment/run_batch_suite.py'...")
    print("This may take a long time. You can monitor the console for progress.")
    print("--------------------------------------------------\n")

    try:
        # Create a copy of the current environment and force UTF-8 for the child process
        child_env = os.environ.copy()
        child_env['PYTHONIOENCODING'] = 'utf-8'

        # Correctly run the batch suite as a module to ensure proper package imports
        # Instead of using -m, let's call the script directly to avoid module import issues
        command = [sys.executable, os.path.join(os.path.dirname(__file__), "run_batch_suite.py")]
        if debug_mode:
            command.append("--debug")

        # Start the subprocess with the corrected environment
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                   text=True, encoding='utf-8', env=child_env, errors='replace')

        # Stream output correctly
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                try:
                    print(output.strip())
                except UnicodeDecodeError:
                    # Handle any remaining decode errors by replacing problematic characters
                    print(output.encode('utf-8', errors='replace').decode('utf-8').strip())
        
        rc = process.poll()
        if rc == 0:
            print("\n--------------------------------------------------")
            print("Batch suite completed successfully!")
            print("Check SUMMARY_REPORT.md for an overview.")
            print("--------------------------------------------------")
            
            # --- NEW: Automatically run analysis if requested ---
            if auto_analyze:
                print("\n--- 启动自动分析流程 ---")
                success = run_automatic_analysis()
                if success:
                    print("自动分析已成功启动并完成。")
                else:
                    print("自动分析启动失败或在执行过程中遇到错误。")
            # --- END NEW ---
            
        else:
            print(f"\nBatch suite finished with errors (exit code: {rc}).")

    except FileNotFoundError:
        print("Error: Could not find 'llm_assessment/run_batch_suite.py'.")
    except Exception as e:
        print(f"An unexpected error occurred during execution: {e}")

# --- NEW: Automatic Analysis Function ---
import importlib.util
import sys
import os
import subprocess

def run_automatic_analysis():
    """Attempts to run the shared analysis module using all available evaluators."""
    try:
        print("\n--- 启动自动分析流程 ---")
        
        # 1. Find the latest result file
        print("正在查找最近生成的测评结果文件...")
        results_dir = "results"
        if not os.path.exists(results_dir):
            print(f"Error: Results directory '{results_dir}' not found.")
            return False

        result_files = [os.path.join(results_dir, f) for f in os.listdir(results_dir) if f.endswith('.json')]
        if not result_files:
            print("未在 'results/' 目录下找到任何 .json 结果文件。")
            return False

        result_files.sort(key=os.path.getmtime, reverse=True)
        latest_result_file = result_files[0]
        print(f"找到最新结果文件: {latest_result_file}")

        # 2. Determine available evaluators by parsing .env
        config = load_evaluator_config_from_env()
        available_evaluators = get_available_evaluators(config)
        
        if not available_evaluators:
            print("警告: 未检测到可用的评估器。请检查.env文件是否正确配置了API密钥。")
            return False
            
        print(f"检测到可用的评估器: {', '.join(available_evaluators)}")
        
        # 3. Run the analysis for each available evaluator
        success_count = 0
        for evaluator in available_evaluators:
            print(f"\n--- 使用评估器 '{evaluator}' 进行分析 ---")
            try:
                # Run comprehensive analysis with the current evaluator
                cmd = [
                    sys.executable, 
                    os.path.join(os.path.dirname(__file__), "comprehensive_big5_analysis.py"),
                    "--input", latest_result_file,
                    "--evaluator", evaluator
                ]
                
                print(f"执行命令: {' '.join(cmd)}")
                result = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8')
                print(result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)
                success_count += 1
                print(f"'{evaluator}' 评估器分析完成。")
            except subprocess.CalledProcessError as e:
                print(f"使用 '{evaluator}' 评估器时出错:")
                print(f"命令: {' '.join(e.cmd)}")
                print(f"返回码: {e.returncode}")
                print(f"STDOUT: {e.stdout}")
                print(f"STDERR: {e.stderr}")
            except Exception as e:
                print(f"运行 '{evaluator}' 评估器时发生未知错误: {e}")
        
        if success_count > 0:
            print(f"\n成功使用 {success_count} 个评估器完成了分析。")
            return True
        else:
            print("\n所有评估器的分析都失败了。")
            return False
            
    except Exception as e:
        print(f"自动分析过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False
# --- END NEW ---

from python_utf8_config import ensure_utf8

if __name__ == "__main__":
    ensure_utf8()
    main()