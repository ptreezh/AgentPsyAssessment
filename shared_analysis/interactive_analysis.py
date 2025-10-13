#!/usr/bin/env python3
"""
Interactive analysis and assessment tool for psychological tests.
This script provides a unified interface for both analyzing existing results
and running new assessments. It's designed to be a convenient entry point
for users who want to explore the capabilities of the AgentPsy framework.

Note:
As of 2025-08-23, the '--mode assessment' functionality has been REMOVED from this script.
The assessment execution logic has been moved to the dedicated `llm_assessment` module
to maintain a clear separation of concerns and reduce redundancy.

For running new assessments, please use the scripts in the `llm_assessment` directory:
- `llm_assessment/interactive_cli_runner.py` (Interactive mode)
- `llm_assessment/run_assessment_unified.py` (Script mode)

This script now focuses SOLELY on the '--mode analysis' functionality.
"""

import sys
import os
import json
import argparse
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import time

# Add the parent directory to the Python path so we can import modules
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Add the parent directory to the Python path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import analysis functions
from shared_analysis.analyze_results import (
    load_evaluator_config, 
    analyze_single_file,
    generate_individual_report,
    save_scores_as_json,
    generate_disagreement_report
)

# --- Constants ---
RESULTS_DIR = "results"
REPORTS_DIR = "analysis_reports"
ROLES_DIR = "llm_assessment/roles"
TESTS_DIR = "llm_assessment/test_files"
LOGS_DIR = "logs"

EVALUATOR_PROVIDERS = ["gpt", "claude", "gemini", "deepseek", "glm"]

# --- Helper Functions for Analysis Mode ---

def get_available_files(directory: str, extension: str = ".json") -> List[str]:
    """Get list of available files in a directory"""
    files = []
    if os.path.exists(directory):
        for file in os.listdir(directory):
            if file.endswith(extension):
                files.append(file)
    return files

def select_single_option(options: List[str], prompt: str) -> str:
    """Let user select a single option from a list"""
    if not options:
        print("No options available.")
        return ""
    
    print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    
    while True:
        try:
            selection = input("\n请输入选项编号: ").strip()
            if selection.lower() == 'q':
                print("退出程序。")
                sys.exit(0)
                
            selection = int(selection) - 1
            if 0 <= selection < len(options):
                return options[selection]
            else:
                print("输入有误，请输入有效的选项编号。")
        except ValueError:
            print("输入有误，请输入有效的选项编号。")
        except EOFError:
            # When EOF is encountered (e.g., in non-interactive environments)
            print("\n无法读取用户输入，将使用第一个选项作为默认选择。")
            return options[0] if options else ""

def select_multiple_options(options: List[str], prompt: str) -> List[str]:
    """Let user select multiple options from a list"""
    if not options:
        print("No options available.")
        return []
        
    print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    
    while True:
        try:
            selection = input("\n请输入选项编号（可多选，用逗号分隔，输入'all'选择全部，输入'q'退出）: ").strip()
            if selection.lower() == 'q':
                print("退出程序。")
                sys.exit(0)
                
            if selection.lower() == 'all':
                return options
                
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
            if all(0 <= idx < len(options) for idx in indices):
                return [options[idx] for idx in indices]
            else:
                print("输入有误，请输入有效的选项编号。")
        except ValueError:
            print("输入有误，请输入有效的选项编号或'all'。")
        except EOFError:
            # When EOF is encountered (e.g., in non-interactive environments)
            print("\n无法读取用户输入，将使用所有选项作为默认选择。")
            return options

def get_available_results() -> List[str]:
    """Get list of available result files"""
    return get_available_files(RESULTS_DIR)

def get_available_roles() -> List[str]:
    """Get list of available role files"""
    roles = ['default']  # Always include default option
    if os.path.exists(ROLES_DIR):
        for file in os.listdir(ROLES_DIR):
            if file.endswith('.txt'):
                roles.append(file[:-4])  # Remove .txt extension
    return roles

def display_evaluator_status(config: Dict[str, Any]) -> None:
    """Display the status of all evaluators"""
    print("\n=== 评估器状态 ===")
    for evaluator in EVALUATOR_PROVIDERS:
        model_id_key = f"{evaluator}_model_id"
        api_key_key = f"{evaluator}_api_key"
        
        model_id = config.get(model_id_key, "Not set")
        api_key = config.get(api_key_key, "Not set")
        
        # Special handling for specific evaluators
        if evaluator == "glm" and api_key == "Not set":
            api_key = config.get("glm_api_key", "Not set")
        elif evaluator == "deepseek" and api_key == "Not set":
            api_key = config.get("deepseek_api_key", "Not set") or config.get("modelscope_api_key", "Not set")
        elif evaluator == "gemini" and api_key == "Not set":
            api_key = config.get("google_api_key", "Not set")
        elif evaluator == "claude" and api_key == "Not set":
            api_key = config.get("anthropic_api_key", "Not set")
            
        status = "[可用]" if api_key != "Not set" else "[未配置]"
        print(f"  {evaluator.upper():8} | {model_id:25} | {status}")

# --- Main Analysis Runner ---

def run_interactive_analysis():
    """Main interactive analysis function"""
    print("=== AgentPsy 心理测评结果分析工具 ===")
    print("此工具将分析results目录下的测评结果，并生成评估报告。")
    
    # Load configuration
    config = load_evaluator_config()
    
    # Display evaluator status
    display_evaluator_status(config)
    
    # Get available result files
    result_files = get_available_results()
    
    if not result_files:
        print("\n未找到结果文件。请先运行测评以生成结果文件。")
        return
    
    # Select result file
    result_file = select_single_option(
        result_files, 
        "请选择要分析的结果文件:"
    )
    
    if not result_file:
        print("未选择结果文件，退出程序。")
        return
        
    result_file_path = os.path.join(RESULTS_DIR, result_file)
    if not os.path.exists(result_file_path):
        print(f"结果文件不存在: {result_file_path}")
        return
    
    # Select evaluators
    available_evaluators = [e for e in EVALUATOR_PROVIDERS if config.get(f"{e}_api_key") or 
                           (e == "glm" and config.get("glm_api_key")) or
                           (e == "deepseek" and (config.get("deepseek_api_key") or config.get("modelscope_api_key"))) or
                           (e == "gemini" and config.get("google_api_key")) or
                           (e == "claude" and config.get("anthropic_api_key"))]
    
    if not available_evaluators:
        print("\n没有配置可用的评估器。请检查.env文件中的API密钥配置。")
        return
    
    selected_evaluators = select_multiple_options(
        available_evaluators,
        "请选择要使用的评估器（可多选）:"
    )
    
    if not selected_evaluators:
        print("未选择评估器，退出程序。")
        return
    
    print(f"\n=== 开始分析 ===")
    print(f"结果文件: {result_file}")
    print(f"评估器: {', '.join(selected_evaluators)}")
    
    # Run analysis
    try:
        test_data, all_analyses = analyze_single_file(result_file_path, selected_evaluators, config)
        
        if not all_analyses:
            print("分析失败，没有生成任何评估结果。")
            return
            
        # Create output directory
        base_filename = os.path.splitext(result_file)[0]
        output_dir = os.path.join(REPORTS_DIR, base_filename)
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate reports
        evaluators_with_results = []
        for evaluator, analysis_data in all_analyses.items():
            # Check if this evaluator has valid results (no error and valid score)
            valid_results = [result for result in analysis_data if isinstance(result, dict) and not result.get("error") and result.get("score", -1) != -1]
            if valid_results or len(valid_results) > len(analysis_data) * 0.5:  # At least 50% valid results
                model_id = config[f"{evaluator}_model_id"]
                generate_individual_report(test_data, analysis_data, evaluator, model_id, output_dir)
                evaluators_with_results.append(evaluator)
            else:
                print(f"跳过 {evaluator} 的报告生成，因为有效结果不足")
        
        # Generate disagreement report if we have more than one evaluator with results
        if len(evaluators_with_results) > 1:
            generate_disagreement_report(
                test_data, 
                {evaluator: all_analyses[evaluator] for evaluator in evaluators_with_results}, 
                output_dir
            )
            print(f"\n分析完成！生成了 {len(evaluators_with_results)} 个评估报告和 1 个分歧报告。")
        elif len(evaluators_with_results) == 1:
            print(f"\n分析完成！生成了 {len(evaluators_with_results)} 个评估报告。")
        else:
            print("\n没有生成任何报告。")
            
        print(f"报告已保存至: {output_dir}")
        
    except Exception as e:
        print(f"分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

# --- Main Execution ---

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Interactive analysis and assessment tool for psychological tests")
    parser.add_argument("--mode", choices=["analysis"], default="analysis", 
                       help="Mode: 'analysis' for analyzing results (assessment mode has been removed, see llm_assessment module)")
    parser.add_argument("--file", help="Directly specify result file to analyze (analysis mode)")
    parser.add_argument("--evaluators", nargs="+", help="Directly specify evaluators to use (analysis mode)")
    parser.add_argument("--cognitive-robustness", "--cr", action="store_true", 
                       help="Run cognitive robustness analysis on a CRTM-compatible log file")
    
    args = parser.parse_args()
    
    # Cognitive Robustness Analysis mode
    if args.cognitive_robustness and args.file:
        # Non-interactive mode for CRTM
        print(f"Running Cognitive Robustness Analysis on: {args.file}")
        log_file_path = args.file
        
        if not os.path.exists(log_file_path):
            print(f"日志文件不存在: {log_file_path}")
            return
            
        # Import and run the cognitive robustness analyzer
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            from shared_analysis.cognitive_robustness_analyzer.main import main as crtm_main
            
            # Generate default output path
            base_name = os.path.splitext(os.path.basename(log_file_path))[0]
            default_output_path = os.path.join(
                os.path.dirname(log_file_path), 
                f"{base_name}_cognitive_robustness_report.md"
            )
            
            # Run the analyzer
            crtm_main(log_file_path, default_output_path)
            print(f"Cognitive Robustness Analysis complete! Report saved to: {default_output_path}")
        except ImportError as e:
            print(f"Error importing cognitive_robustness_analyzer: {e}")
            return
        except Exception as e:
            print(f"Error during Cognitive Robustness Analysis: {e}")
            import traceback
            traceback.print_exc()
            return
    
    # Standard Analysis mode
    elif args.file and args.evaluators:
        # Non-interactive mode
        config = load_evaluator_config()
        result_file_path = os.path.join(RESULTS_DIR, args.file)
        
        if not os.path.exists(result_file_path):
            print(f"结果文件不存在: {result_file_path}")
            return
            
        test_data, all_analyses = analyze_single_file(result_file_path, args.evaluators, config)
        
        # Create output directory
        base_filename = os.path.splitext(args.file)[0]
        output_dir = os.path.join(REPORTS_DIR, base_filename)
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate reports
        evaluators_with_results = []
        for evaluator, analysis_data in all_analyses.items():
            valid_results = [result for result in analysis_data if isinstance(result, dict) and not result.get("error") and result.get("score", -1) != -1]
            if valid_results or len(valid_results) > len(analysis_data) * 0.5:
                model_id = config[f"{evaluator}_model_id"]
                generate_individual_report(test_data, analysis_data, evaluator, model_id, output_dir)
                evaluators_with_results.append(evaluator)
        
        # Generate disagreement report if needed
        if len(evaluators_with_results) > 1:
            generate_disagreement_report(
                test_data, 
                {evaluator: all_analyses[evaluator] for evaluator in evaluators_with_results}, 
                output_dir
            )
            
        print(f"分析完成！报告已保存至: {output_dir}")
    else:
        # Interactive mode
        run_interactive_analysis()

if __name__ == "__main__":
    main()