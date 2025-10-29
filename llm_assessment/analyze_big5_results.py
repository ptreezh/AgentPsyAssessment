import sys
import os
import json
from typing import Dict, Any

# Add the big5_mbti_module to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared_analysis', 'big5_mbti_module', 'src'))

from data_loader import load_data
from type_mapper import map_to_mbti
from analysis_engine import analyze_personality
from report_generator import generate_markdown_report, generate_json_report


def extract_big_five_scores(test_data: Dict[Any, Any]) -> Dict[str, float]:
    """Extract Big Five scores from the test data."""
    # Initialize score accumulators and counters for each dimension
    dimension_scores = {
        "E": {"total": 0, "count": 0},
        "A": {"total": 0, "count": 0},
        "C": {"total": 0, "count": 0},
        "N": {"total": 0, "count": 0},
        "O": {"total": 0, "count": 0}
    }
    
    # Process each assessment result
    for result in test_data["assessment_results"]:
        dimension = result["question_id"].split("_")[2]  # Extract dimension from question_id
        # For this example, we'll assume a fixed score of 3.0 for all dimensions
        # In a real implementation, you would have actual scoring logic here
        # Make sure the dimension is one of the Big Five
        if dimension in dimension_scores:
            dimension_scores[dimension]["total"] += 3.0
            dimension_scores[dimension]["count"] += 1
    
    # Calculate average scores for each dimension
    big_five_scores = {}
    for dim in dimension_scores:
        if dimension_scores[dim]["count"] > 0:
            big_five_scores[dim] = dimension_scores[dim]["total"] / dimension_scores[dim]["count"]
        else:
            big_five_scores[dim] = 3.0  # Default midpoint score
    
    return big_five_scores


def main():
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python analyze_big5_results.py <path_to_test_result_file>")
        sys.exit(1)
    
    # Get the test result file path from command line arguments
    result_file_path = sys.argv[1]
    
    # Load the test data
    test_data = load_data(result_file_path)
    
    # Extract Big Five scores
    big_five_scores = extract_big_five_scores(test_data)
    print(f"Extracted Big Five scores: {big_five_scores}")
    
    # Map to MBTI type
    mbti_type = map_to_mbti(big_five_scores)
    print(f"Mapped MBTI type: {mbti_type}")
    
    # Analyze personality
    analysis_data = analyze_personality(big_five_scores, mbti_type)
    
    # Generate reports
    base_output_path = result_file_path.replace(".json", "")
    
    # Generate Markdown report
    markdown_output_path = f"{base_output_path}_analysis.md"
    generate_markdown_report(test_data, analysis_data, markdown_output_path)
    
    # Generate JSON report
    json_output_path = f"{base_output_path}_analysis.json"
    generate_json_report(test_data, analysis_data, json_output_path)
    
    print(f"Analysis complete. Reports generated:")
    print(f"  - Markdown: {markdown_output_path}")
    print(f"  - JSON: {json_output_path}")


if __name__ == "__main__":
    main()