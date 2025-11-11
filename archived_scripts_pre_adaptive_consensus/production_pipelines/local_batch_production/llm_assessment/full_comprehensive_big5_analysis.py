#!/usr/bin/env python3
"""
Comprehensive BIG5 Analysis Script
This script processes all BIG5 test results and generates detailed analysis reports.
"""

import os
import json
import subprocess
import sys
from typing import Dict, Any
from collections import defaultdict

# Add the big5_mbti_module to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared_analysis', 'big5_mbti_module', 'src'))

from type_mapper import map_to_mbti
from analysis_engine import analyze_personality


def find_big5_test_files(root_dir: str) -> list:
    """Find all big5 test result files in the results directory and its subdirectories."""
    test_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".json") and "big-five" in file.lower():
                test_files.append(os.path.join(root, file))
    return test_files


def find_big5_scores_files(root_dir: str) -> list:
    """Find all scores.json files in the analysis_reports directory and its subdirectories."""
    scores_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file == "scores.json":
                scores_files.append(os.path.join(root, file))
    return scores_files


def score_test_file(test_file_path: str) -> bool:
    """Score a single test file using analyze_results.py."""
    print(f"Scoring: {test_file_path}")
    
    # Create command to run analyze_results.py
    cmd = [
        "python", 
        "shared_analysis/analyze_results.py", 
        test_file_path, 
        "--evaluators", "qwen"
    ]
    
    try:
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True, cwd="/home/user1/xbots/psy", timeout=300)  # 5 minute timeout
        if result.returncode == 0:
            print(f"  Successfully scored: {test_file_path}")
            return True
        else:
            print(f"  Error scoring {test_file_path}: {result.stderr[:200]}...")  # Limit error output
            return False
    except subprocess.TimeoutExpired:
        print(f"  Timeout while scoring {test_file_path}")
        return False
    except Exception as e:
        print(f"  Exception while scoring {test_file_path}: {e}")
        return False


def load_scores_data(filepath: str) -> Dict[str, Any]:
    """Load scores data from JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def extract_big_five_scores(scores_data: Dict[str, Any]) -> Dict[str, float]:
    """Extract Big Five scores from the scores data."""
    try:
        # We'll use the average scores from the first evaluator
        evaluator_name = list(scores_data["evaluator_scores"].keys())[0]
        full_scores = scores_data["evaluator_scores"][evaluator_name]["average_scores"]
        
        # Convert full names to single letter keys
        converted_scores = {
            "E": full_scores.get("Extraversion", 0),
            "A": full_scores.get("Agreeableness", 0),
            "C": full_scores.get("Conscientiousness", 0),
            "N": full_scores.get("Neuroticism", 0),
            "O": full_scores.get("Openness to Experience", 0)
        }
        
        return converted_scores
    except Exception as e:
        print(f"Error extracting Big Five scores: {e}")
        return None


def analyze_single_report(scores_file_path: str) -> bool:
    """Analyze a single scores.json file."""
    print(f"Analyzing: {scores_file_path}")
    
    # Load the scores data
    scores_data = load_scores_data(scores_file_path)
    if not scores_data:
        return False
    
    # Extract Big Five scores
    big_five_scores = extract_big_five_scores(scores_data)
    if not big_five_scores:
        return False
    
    print(f"  Extracted Big Five scores: {big_five_scores}")
    
    # Map to MBTI type
    mbti_type = map_to_mbti(big_five_scores)
    print(f"  Mapped MBTI type: {mbti_type}")
    
    # Analyze personality
    analysis_data = analyze_personality(big_five_scores, mbti_type)
    
    # Save the analysis results to a JSON file
    output_path = scores_file_path.replace("scores.json", "big5_mbti_analysis.json")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2)
        print(f"  Analysis complete. Results saved to: {output_path}")
        return True
    except Exception as e:
        print(f"  Error saving analysis results: {e}")
        return False


def extract_test_info_from_path(file_path: str) -> dict:
    """Extract model, role, and interference level from file path."""
    # Example path: results/Interactive_Suite_20250826_175341/gemma3_latest_agent-big-five-50-complete2_b10_3i/test.json
    parts = file_path.split("/")
    
    # Extract directory name which contains the test info
    dir_name = parts[-2]  # e.g., gemma3_latest_agent-big-five-50-complete2_b10_3i
    
    # Extract model (everything before the first underscore)
    model_parts = dir_name.split("_")
    model = model_parts[0] + ":" + model_parts[1]  # e.g., gemma3:latest
    
    # Extract role and interference level from the end of directory name
    role = "default"
    interference = 0
    
    # Split by underscores and look for pattern at the end
    name_parts = dir_name.split("_")
    if len(name_parts) >= 3:
        # Check if the last part ends with 'i' (interference level)
        if name_parts[-1].endswith("i"):
            try:
                interference = int(name_parts[-1][:-1])  # Remove 'i' and convert to int
                role = name_parts[-2]  # Role is the second to last part
            except:
                pass
        # If the last part doesn't end with 'i', check if second to last does
        elif len(name_parts) >= 4 and name_parts[-2].endswith("i"):
            try:
                interference = int(name_parts[-2][:-1])  # Remove 'i' and convert to int
                role = name_parts[-3]  # Role is the third to last part
            except:
                pass
    
    return {
        "model": model,
        "role": role,
        "interference": interference
    }


def generate_detailed_summary_report(analyzed_files: list, output_dir: str):
    """Generate a detailed summary report of all analyzed files."""
    summary_data = []
    
    for file_path in analyzed_files:
        try:
            # Load the analysis data
            analysis_path = file_path.replace("scores.json", "big5_mbti_analysis.json")
            with open(analysis_path, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            # Load the scores data
            with open(file_path, 'r', encoding='utf-8') as f:
                scores_data = json.load(f)
            
            # Extract Big Five scores
            big_five_scores = extract_big_five_scores(scores_data)
            
            # Extract MBTI type
            mbti_type = map_to_mbti(big_five_scores)
            
            # Extract test info from path
            test_info = extract_test_info_from_path(file_path)
            
            # Add to summary
            summary_data.append({
                "file_path": file_path,
                "model": test_info["model"],
                "role": test_info["role"],
                "interference_level": test_info["interference"],
                "big_five_scores": big_five_scores,
                "mbti_type": mbti_type,
                "core_strengths": analysis_data["profile"]["core_strengths"],
                "growth_areas": analysis_data["profile"]["growth_areas"]
            })
        except Exception as e:
            print(f"Error processing {file_path} for summary: {e}")
    
    # Save detailed summary report
    summary_path = os.path.join(output_dir, "big5_mbti_analysis_detailed_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    
    print(f"Detailed summary report saved to: {summary_path}")
    
    return summary_data


def generate_model_comparison_report(summary_data: list, output_dir: str):
    """Generate a model comparison report."""
    # Group data by model
    model_data = defaultdict(list)
    for item in summary_data:
        model_data[item["model"]].append(item)
    
    # Generate comparison report
    comparison_path = os.path.join(output_dir, "big5_model_comparison.md")
    with open(comparison_path, 'w', encoding='utf-8') as f:
        f.write("# BIG5 Model Comparison Report\n\n")
        
        for model, items in model_data.items():
            f.write(f"## {model}\n\n")
            f.write("| Role | Interference | MBTI Type | Extraversion | Agreeableness | Conscientiousness | Neuroticism | Openness |\n")
            f.write("|------|--------------|-----------|--------------|---------------|-------------------|-------------|----------|\n")
            
            for item in items:
                scores = item["big_five_scores"]
                f.write(f"| {item['role']} | {item['interference_level']} | {item['mbti_type']} | {scores.get('E', 0):.2f} | {scores.get('A', 0):.2f} | {scores.get('C', 0):.2f} | {scores.get('N', 0):.2f} | {scores.get('O', 0):.2f} |\n")
            
            f.write("\n")
    
    print(f"Model comparison report saved to: {comparison_path}")


def generate_role_analysis_report(summary_data: list, output_dir: str):
    """Generate a role analysis report."""
    # Group data by role
    role_data = defaultdict(list)
    for item in summary_data:
        role_data[item["role"]].append(item)
    
    # Generate role analysis report
    role_path = os.path.join(output_dir, "big5_role_analysis.md")
    with open(role_path, 'w', encoding='utf-8') as f:
        f.write("# BIG5 Role Analysis Report\n\n")
        
        for role, items in role_data.items():
            f.write(f"## Role: {role}\n\n")
            f.write("| Model | Interference | MBTI Type | Extraversion | Agreeableness | Conscientiousness | Neuroticism | Openness |\n")
            f.write("|-------|--------------|-----------|--------------|---------------|-------------------|-------------|----------|\n")
            
            for item in items:
                scores = item["big_five_scores"]
                f.write(f"| {item['model']} | {item['interference_level']} | {item['mbti_type']} | {scores.get('E', 0):.2f} | {scores.get('A', 0):.2f} | {scores.get('C', 0):.2f} | {scores.get('N', 0):.2f} | {scores.get('O', 0):.2f} |\n")
            
            f.write("\n")
    
    print(f"Role analysis report saved to: {role_path}")


def generate_interference_impact_report(summary_data: list, output_dir: str):
    """Generate an interference impact report."""
    # Group data by model and role, then sort by interference level
    interference_data = defaultdict(list)
    for item in summary_data:
        key = f"{item['model']}_{item['role']}"
        interference_data[key].append(item)
    
    # Sort each group by interference level
    for key in interference_data:
        interference_data[key].sort(key=lambda x: x["interference_level"])
    
    # Generate interference impact report
    interference_path = os.path.join(output_dir, "big5_interference_impact.md")
    with open(interference_path, 'w', encoding='utf-8') as f:
        f.write("# BIG5 Interference Impact Report\n\n")
        f.write("This report shows how different interference levels affect personality scores.\n\n")
        
        for key, items in interference_data.items():
            if len(items) > 1:  # Only show items with multiple interference levels
                model, role = key.split("_", 1)
                f.write(f"## {model} - Role: {role}\n\n")
                f.write("| Interference | MBTI Type | Extraversion | Agreeableness | Conscientiousness | Neuroticism | Openness |\n")
                f.write("|--------------|-----------|--------------|---------------|-------------------|-------------|----------|\n")
                
                for item in items:
                    scores = item["big_five_scores"]
                    f.write(f"| {item['interference_level']} | {item['mbti_type']} | {scores.get('E', 0):.2f} | {scores.get('A', 0):.2f} | {scores.get('C', 0):.2f} | {scores.get('N', 0):.2f} | {scores.get('O', 0):.2f} |\n")
                
                f.write("\n")
    
    print(f"Interference impact report saved to: {interference_path}")


def generate_summary_report(summary_data: list, output_dir: str):
    """Generate the main summary report."""
    summary_path = os.path.join(output_dir, "big5_mbti_analysis_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    
    print(f"Summary report saved to: {summary_path}")
    
    # Also generate a markdown summary
    markdown_path = os.path.join(output_dir, "big5_mbti_analysis_summary.md")
    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write("# BIG5 to MBTI Analysis Summary\n\n")
        f.write("| Model | Role | Interference | MBTI Type | Extraversion | Agreeableness | Conscientiousness | Neuroticism | Openness |\n")
        f.write("|-------|------|--------------|-----------|--------------|---------------|-------------------|-------------|----------|\n")
        
        for item in summary_data:
            scores = item["big_five_scores"]
            f.write(f"| {item['model']} | {item['role']} | {item['interference_level']} | {item['mbti_type']} | {scores.get('E', 0):.2f} | {scores.get('A', 0):.2f} | {scores.get('C', 0):.2f} | {scores.get('N', 0):.2f} | {scores.get('O', 0):.2f} |\n")
    
    print(f"Markdown summary saved to: {markdown_path}")


def main():
    print("=== Comprehensive BIG5 Analysis Script ===")
    
    # Step 1: Find all big5 test result files
    results_dir = "results"
    if not os.path.exists(results_dir):
        print(f"Results directory '{results_dir}' not found.")
        return
    
    test_files = find_big5_test_files(results_dir)
    if not test_files:
        print("No big5 test result files found in the results directory.")
        return
    
    print(f"Found {len(test_files)} big5 test result files to score.")
    
    # For demo purposes, let's process a limited number of files
    # In a full run, we would process all files
    test_files_to_process = test_files[:10]  # Process first 10 files for demo
    print(f"Processing {len(test_files_to_process)} files for demo...")
    
    # Score each test file
    scored_files = []
    for test_file in test_files_to_process:
        if score_test_file(test_file):
            scored_files.append(test_file)
    
    print(f"\nSuccessfully scored {len(scored_files)} files.")
    
    # Step 2: Find all scores.json files
    analysis_reports_dir = "analysis_reports"
    scores_files = find_big5_scores_files(analysis_reports_dir)
    if not scores_files:
        print("No scores.json files found in the analysis_reports directory.")
        return
    
    print(f"Found {len(scores_files)} scores.json files to analyze.")
    
    # Analyze each scores file
    analyzed_files = []
    for scores_file in scores_files:
        if analyze_single_report(scores_file):
            analyzed_files.append(scores_file)
    
    print(f"\nSuccessfully analyzed {len(analyzed_files)} files.")
    
    # Generate reports
    if analyzed_files:
        os.makedirs("analysis_reports", exist_ok=True)
        
        # Generate detailed summary
        summary_data = generate_detailed_summary_report(analyzed_files, "analysis_reports")
        
        # Generate various reports
        generate_summary_report(summary_data, "analysis_reports")
        generate_model_comparison_report(summary_data, "analysis_reports")
        generate_role_analysis_report(summary_data, "analysis_reports")
        generate_interference_impact_report(summary_data, "analysis_reports")
        
        print("\n=== Analysis Complete ===")
        print(f"Generated {len(summary_data)} analysis reports.")
        print("Reports saved in: analysis_reports/")


if __name__ == "__main__":
    main()