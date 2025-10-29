import sys
import os
import json
from typing import Dict, Any

# Add the big5_mbti_module to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared_analysis', 'big5_mbti_module', 'src'))

from type_mapper import map_to_mbti
from analysis_engine import analyze_personality


def load_scores_data(filepath: str) -> Dict[str, Any]:
    """Load scores data from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_big_five_scores(scores_data: Dict[str, Any]) -> Dict[str, float]:
    """Extract Big Five scores from the scores data."""
    # We'll use the average scores from the first evaluator
    evaluator_name = list(scores_data["evaluator_scores"].keys())[0]
    return scores_data["evaluator_scores"][evaluator_name]["average_scores"]


def main():
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python analyze_big5_with_module.py <path_to_scores_file>")
        sys.exit(1)
    
    # Get the scores file path from command line arguments
    scores_file_path = sys.argv[1]
    
    # Load the scores data
    scores_data = load_scores_data(scores_file_path)
    
    # Extract Big Five scores
    big_five_scores = extract_big_five_scores(scores_data)
    print(f"Extracted Big Five scores: {big_five_scores}")
    
    # Map to MBTI type
    mbti_type = map_to_mbti(big_five_scores)
    print(f"Mapped MBTI type: {mbti_type}")
    
    # Analyze personality
    analysis_data = analyze_personality(big_five_scores, mbti_type)
    
    # Save the analysis results to a JSON file
    output_path = scores_file_path.replace("scores.json", "big5_mbti_analysis.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, ensure_ascii=False, indent=2)
    
    print(f"Analysis complete. Results saved to: {output_path}")
    
    # Print some key insights
    print("\nKey Insights:")
    print(f"Core Strengths: {analysis_data['profile']['core_strengths']}")
    print(f"Growth Areas: {analysis_data['profile']['growth_areas']}")
    print(f"Communication Style: {analysis_data['communication']['communication_style']}")


if __name__ == "__main__":
    main()