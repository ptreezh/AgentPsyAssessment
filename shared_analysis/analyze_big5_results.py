import sys
import os
import json
from typing import Dict, Any
from datetime import datetime

# Add debug flag
DEBUG = True

def debug_print(message):
    """Debug print function."""
    if DEBUG:
        print(f"[DEBUG] {message}")

# Try to import the big5_mbti_module, fallback to basic functionality if not available
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared_analysis', 'big5_mbti_module', 'src'))
    from data_loader import load_data
    from type_mapper import map_to_mbti
    from analysis_engine import analyze_personality
    from report_generator import generate_markdown_report, generate_json_report
    MODULE_AVAILABLE = True
    debug_print("Successfully imported big5_mbti_module")
except ImportError as e:
    debug_print(f"Failed to import big5_mbti_module: {e}")
    MODULE_AVAILABLE = False


def extract_big_five_scores(test_data: Dict[Any, Any]) -> Dict[str, float]:
    """Extract Big Five scores from the test data."""
    debug_print("Extracting Big Five scores from test data")
    
    # Initialize score accumulators and counters for each dimension
    dimension_scores = {
        "E": {"total": 0, "count": 0},
        "A": {"total": 0, "count": 0},
        "C": {"total": 0, "count": 0},
        "N": {"total": 0, "count": 0},
        "O": {"total": 0, "count": 0}
    }
    
    # Process each assessment result
    assessment_results = test_data.get("assessment_results", [])
    debug_print(f"Found {len(assessment_results)} assessment results")
    
    for i, result in enumerate(assessment_results):
        debug_print(f"Processing result {i+1}: {result.get('question_id', 'Unknown ID')}")
        
        # Handle different data formats
        question_data = result.get("question_data", {})
        if question_data:
            # New format: dimension info is in question_data
            question_id = question_data.get("question_id", "")
            dimension = question_data.get("dimension", "")
            debug_print(f"  Found question_data: {question_id}, dimension: {dimension}")
        else:
            # Old format: dimension info is directly in result
            question_id = result.get("question_id", "")
            if not question_id:
                debug_print(f"  Skipping result {i+1}: no question_id")
                continue
                
            # Handle different question_id formats (string or integer)
            if isinstance(question_id, int):
                question_id = str(question_id)
            
            parts = question_id.split("_")
            if len(parts) < 3:
                # Try to extract dimension from other fields
                dimension = result.get("dimension", "")
                if not dimension:
                    debug_print(f"  Skipping result {i+1}: cannot determine dimension")
                    continue
            else:
                dimension = parts[2]  # Extract dimension from question_id
            
        # Map dimension abbreviations to full names
        dimension_mapping = {
            "E": "E", "Extraversion": "E",
            "A": "A", "Agreeableness": "A", 
            "C": "C", "Conscientiousness": "C",
            "N": "N", "Neuroticism": "N",
            "O": "O", "Openness": "O", "Openness to Experience": "O"
        }
        
        # Normalize dimension name
        dimension = dimension_mapping.get(dimension, dimension)
        
        # Check if it's a valid Big Five dimension
        if dimension not in ["E", "A", "C", "N", "O"]:
            debug_print(f"  Skipping result {i+1}: unknown dimension '{dimension}'")
            continue
        
        # For this example, we'll assume a fixed score of 3.0 for all dimensions
        # In a real implementation, you would have actual scoring logic here
        # Make sure the dimension is one of the Big Five
        if dimension in dimension_scores:
            score = 3.0  # Default score
            dimension_scores[dimension]["total"] += score
            dimension_scores[dimension]["count"] += 1
            debug_print(f"  Added score {score} for dimension {dimension}")
        else:
            debug_print(f"  Unknown dimension: {dimension}")
    
    # Calculate average scores for each dimension
    big_five_scores = {}
    for dim in dimension_scores:
        if dimension_scores[dim]["count"] > 0:
            big_five_scores[dim] = dimension_scores[dim]["total"] / dimension_scores[dim]["count"]
        else:
            big_five_scores[dim] = 3.0  # Default midpoint score
        debug_print(f"  {dim}: {big_five_scores[dim]:.2f} (from {dimension_scores[dim]['count']} questions)")
    
    debug_print(f"Final Big Five scores: {big_five_scores}")
    return big_five_scores


def load_data_fallback(filepath: str) -> Dict[Any, Any]:
    """Fallback data loading function."""
    debug_print(f"Loading data from: {filepath}")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        debug_print(f"Successfully loaded data with {len(data)} keys")
        return data
    except json.JSONDecodeError as e:
        debug_print(f"JSON decode error: {e}")
        raise
    except Exception as e:
        debug_print(f"Error loading data: {e}")
        raise

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

def generate_reports_fallback(test_data, analysis_data, base_output_path):
    """Generate basic reports without the full module."""
    debug_print(f"Generating reports with base path: {base_output_path}")
    
    # Generate JSON report
    json_output_path = f"{base_output_path}_analysis.json"
    try:
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "test_data": test_data,
                "analysis": analysis_data,
                "generated_at": datetime.now().isoformat(),
                "module_used": "fallback"
            }, f, ensure_ascii=False, indent=2)
        print(f"JSON report saved to: {json_output_path}")
    except Exception as e:
        debug_print(f"Error saving JSON report: {e}")
    
    # Generate Markdown report
    markdown_output_path = f"{base_output_path}_analysis.md"
    try:
        with open(markdown_output_path, 'w', encoding='utf-8') as f:
            f.write("# Big Five Personality Analysis\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**MBTI Type:** {analysis_data['profile']['mbti_type']}\n\n")
            f.write("## Big Five Scores\n\n")
            
            if 'big_five_scores' in analysis_data:
                scores = analysis_data['big_five_scores']
                f.write("| Dimension | Score |\n")
                f.write("|-----------|-------|\n")
                for dim, score in scores.items():
                    f.write(f"| {dim} | {score:.2f} |\n")
            
            f.write("\n## Core Strengths\n\n")
            for strength in analysis_data['profile']['core_strengths']:
                f.write(f"- {strength}\n")
            
            f.write("\n## Growth Areas\n\n")
            for area in analysis_data['profile']['growth_areas']:
                f.write(f"- {area}\n")
            
        print(f"Markdown report saved to: {markdown_output_path}")
    except Exception as e:
        debug_print(f"Error saving Markdown report: {e}")

def main():
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python analyze_big5_results.py <path_to_test_result_file>")
        sys.exit(1)
    
    # Get the test result file path from command line arguments
    result_file_path = sys.argv[1]
    
    # Load the test data
    if MODULE_AVAILABLE:
        test_data = load_data(result_file_path)
    else:
        test_data = load_data_fallback(result_file_path)
    
    # Extract Big Five scores
    big_five_scores = extract_big_five_scores(test_data)
    print(f"Extracted Big Five scores: {big_five_scores}")
    
    # Map to MBTI type
    if MODULE_AVAILABLE:
        mbti_type = map_to_mbti(big_five_scores)
    else:
        mbti_type = map_to_mbti_fallback(big_five_scores)
    print(f"Mapped MBTI type: {mbti_type}")
    
    # Analyze personality
    if MODULE_AVAILABLE:
        analysis_data = analyze_personality(big_five_scores, mbti_type)
    else:
        analysis_data = analyze_personality_fallback(big_five_scores, mbti_type)
        # Add scores to analysis for reporting
        analysis_data['big_five_scores'] = big_five_scores
    
    # Generate reports
    base_output_path = result_file_path.replace(".json", "")
    
    if MODULE_AVAILABLE:
        # Generate Markdown report
        markdown_output_path = f"{base_output_path}_analysis.md"
        generate_markdown_report(test_data, analysis_data, markdown_output_path)
        
        # Generate JSON report
        json_output_path = f"{base_output_path}_analysis.json"
        generate_json_report(test_data, analysis_data, json_output_path)
    else:
        generate_reports_fallback(test_data, analysis_data, base_output_path)
    
    print(f"Analysis complete. Reports generated:")
    if MODULE_AVAILABLE:
        print(f"  - Markdown: {markdown_output_path}")
        print(f"  - JSON: {json_output_path}")
    else:
        print(f"  - Using fallback mode (big5_mbti_module not available)")


if __name__ == "__main__":
    main()