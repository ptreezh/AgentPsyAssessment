import os
import json
import subprocess
import sys
import argparse
from typing import Dict, Any

# Add debug flag
DEBUG = True

def debug_print(message):
    """Debug print function."""
    if DEBUG:
        print(f"[DEBUG] {message}")

# Try to import the big5_mbti_module, fallback to basic functionality if not available
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared_analysis', 'big5_mbti_module', 'src'))
    from type_mapper import map_to_mbti
    from analysis_engine import analyze_personality
    MODULE_AVAILABLE = True
    debug_print("Successfully imported big5_mbti_module")
except ImportError as e:
    debug_print(f"Failed to import big5_mbti_module: {e}")
    MODULE_AVAILABLE = False

# Fallback functions
def map_to_mbti_fallback(scores: Dict[str, float]) -> str:
    """Fallback MBTI mapping function."""
    debug_print(f"Mapping scores to MBTI: {scores}")
    
    # Simple MBTI mapping based on scores
    E = scores.get('E', 3.0)
    I = 5.0 - E  # Invert extraversion for introversion
    
    S = 3.0  # Default sensing
    N = 3.0  # Default intuition
    
    T = scores.get('T', 3.0) if 'T' in scores else scores.get('C', 3.0)  # Use thinking or conscientiousness
    F = 5.0 - T  # Invert for feeling
    
    J = scores.get('C', 3.0)  # Use conscientiousness for judging
    P = 5.0 - J  # Invert for perceiving
    
    # Determine preferences
    mbti = ""
    mbti += "E" if E > I else "I"
    mbti += "S" if S > N else "N"
    mbti += "T" if T > F else "F"
    mbti += "J" if J > P else "P"
    
    debug_print(f"Calculated MBTI: {mbti}")
    return mbti

def analyze_personality_fallback(scores: Dict[str, float], mbti_type: str) -> Dict[Any, Any]:
    """Fallback personality analysis function."""
    debug_print(f"Analyzing personality with scores: {scores}, MBTI: {mbti_type}")
    
    # Simple personality analysis
    analysis = {
        "profile": {
            "mbti_type": mbti_type,
            "core_strengths": [],
            "growth_areas": []
        },
        "communication": {
            "communication_style": "Balanced",
            "preferred_interaction": "Flexible"
        },
        "work_style": {
            "work_approach": "Methodical",
            "team_preference": "Collaborative"
        }
    }
    
    # Add strengths based on scores
    if scores.get('E', 3.0) > 3.5:
        analysis["profile"]["core_strengths"].append("Social engagement")
    if scores.get('A', 3.0) > 3.5:
        analysis["profile"]["core_strengths"].append("Cooperation")
    if scores.get('C', 3.0) > 3.5:
        analysis["profile"]["core_strengths"].append("Organization")
    
    # Add growth areas
    if scores.get('N', 3.0) < 2.5:
        analysis["profile"]["growth_areas"].append("Openness to new experiences")
    if scores.get('C', 3.0) < 2.5:
        analysis["profile"]["growth_areas"].append("Attention to detail")
    
    debug_print(f"Generated analysis: {analysis}")
    return analysis


def find_big5_test_files(root_dir: str) -> list:
    test_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".json") and "big-five" in file.lower():
                test_files.append(os.path.join(root, file))
    return test_files


def find_big5_scores_files(root_dir: str) -> list:
    scores_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file == "scores.json":
                scores_files.append(os.path.join(root, file))
    return scores_files


def score_test_file(test_file_path: str) -> bool:
    print(f"Scoring: {test_file_path}")
    
    # Create command to run analyze_results.py
    # We'll use the qwen evaluator since we know it works
    cmd = [
        "python", 
        "shared_analysis/analyze_results.py", 
        test_file_path, 
        "--evaluators", "qwen"
    ]
    
    try:
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  Successfully scored: {test_file_path}")
            return True
        else:
            print(f"  Error scoring {test_file_path}: {result.stderr}")
            return False
    except Exception as e:
        print(f"  Exception while scoring {test_file_path}: {e}")
        return False


def score_test_file_with_evaluator(test_file_path: str, evaluator: str) -> bool:
    print(f"Scoring: {test_file_path} with evaluator: {evaluator}")
    
    # Create command to run analyze_results.py with the specified evaluator
    cmd = [
        "python", 
        "shared_analysis/analyze_results.py", 
        test_file_path, 
        "--evaluators", evaluator
    ]
    
    try:
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  Successfully scored: {test_file_path}")
            return True
        else:
            print(f"  Error scoring {test_file_path}: {result.stderr}")
            return False
    except Exception as e:
        print(f"  Exception while scoring {test_file_path}: {e}")
        return False


def load_scores_data(filepath: str) -> Dict[str, Any]:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def extract_big_five_scores(scores_data: Dict[str, Any]) -> Dict[str, float]:
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
    print(f"Analyzing: {scores_file_path}")
    
    scores_data = load_scores_data(scores_file_path)
    if not scores_data:
        return False
    
    big_five_scores = extract_big_five_scores(scores_data)
    if not big_five_scores:
        return False
    
    print(f"  Extracted Big Five scores: {big_five_scores}")
    
    # Use appropriate MBTI mapping function
    if MODULE_AVAILABLE:
        mbti_type = map_to_mbti(big_five_scores)
    else:
        mbti_type = map_to_mbti_fallback(big_five_scores)
    print(f"  Mapped MBTI type: {mbti_type}")
    
    # Use appropriate personality analysis function
    if MODULE_AVAILABLE:
        analysis_data = analyze_personality(big_five_scores, mbti_type)
    else:
        analysis_data = analyze_personality_fallback(big_five_scores, mbti_type)
        # Add scores to analysis for reporting
        analysis_data['big_five_scores'] = big_five_scores
    
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
    # Example path: results/Interactive_Suite_20250826_175341/gemma3_latest_agent-big-five-50-complete2_b10_3i
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


def generate_summary_report(analyzed_files: list, output_dir: str):
    summary_data = []
    
    for file_path in analyzed_files:
        try:
            analysis_path = file_path.replace("scores.json", "big5_mbti_analysis.json")
            with open(analysis_path, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                scores_data = json.load(f)
            
            big_five_scores = extract_big_five_scores(scores_data)
            if MODULE_AVAILABLE:
                mbti_type = map_to_mbti(big_five_scores)
            else:
                mbti_type = map_to_mbti_fallback(big_five_scores)
            test_info = extract_test_info_from_path(file_path)
            
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
    
    summary_path = os.path.join(output_dir, "big5_mbti_analysis_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    
    print(f"Summary report saved to: {summary_path}")
    
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
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Comprehensive BIG5 to MBTI analysis")
    parser.add_argument("--input", help="Input result file to analyze")
    parser.add_argument("--evaluator", help="Evaluator to use for analysis")
    
    args = parser.parse_args()
    
    # If input file is provided, use it directly
    if args.input:
        print(f"Scoring input file: {args.input}")
        if args.evaluator:
            print(f"Using evaluator: {args.evaluator}")
            # Use the specified evaluator
            if score_test_file_with_evaluator(args.input, args.evaluator):
                print(f"Successfully scored: {args.input}")
            else:
                print(f"Failed to score: {args.input}")
        else:
            # Use default evaluator
            if score_test_file(args.input):
                print(f"Successfully scored: {args.input}")
            else:
                print(f"Failed to score: {args.input}")
        return
    
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
    
    # Score each test file
    scored_files = []
    for test_file in test_files[:5]:  # Limit to first 5 files for testing
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
    
    # Generate summary report
    if analyzed_files:
        os.makedirs("analysis_reports", exist_ok=True)
        generate_summary_report(analyzed_files, "analysis_reports")


if __name__ == "__main__":
    main()