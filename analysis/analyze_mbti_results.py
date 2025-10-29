"""
MBTI analysis script for AgentPsyAssessment
This script provides functions to analyze assessment results specifically for MBTI personality types.
"""

import json
import argparse
import os
from typing import Dict, Any

def analyze_mbti(input_file: str, confidence_threshold: float = 0.7) -> Dict[str, Any]:
    """
    Analyze assessment results for MBTI personality type.
    
    Args:
        input_file: Path to assessment results file
        confidence_threshold: Confidence threshold for recommendations
    
    Returns:
        Dictionary containing MBTI analysis results
    """
    # Load the assessment results
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file does not exist: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        assessment_data = json.load(f)
    
    # Perform MBTI analysis
    result = run_mbti_analysis(assessment_data, confidence_threshold)
    
    # Add metadata to the result
    result.update({
        "input_assessment_id": assessment_data.get("id", "unknown"),
        "analysis_type": "mbti",
        "confidence_threshold": confidence_threshold
    })
    
    # Save results to file
    output_file = f"results/mbti_analysis_{os.path.basename(input_file)}"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"MBTI analysis results saved to: {output_file}")
    return result


def run_mbti_analysis(assessment_data: Dict[str, Any], confidence_threshold: float) -> Dict[str, Any]:
    """Perform detailed MBTI personality analysis."""
    print("Performing MBTI analysis...")
    
    # This is a placeholder implementation - in a real system, this would contain
    # actual analysis logic for MBTI dimensions
    # Extract relevant data from assessment
    responses = assessment_data.get("responses", [])
    
    # Calculate MBTI dimensions (simplified example)
    mbti_dimensions = calculate_mbti_dimensions(responses)
    
    # Determine MBTI type
    mbti_type = determine_mbti_type(mbti_dimensions)
    
    # Generate analysis for each dimension
    mbti_analysis = {}
    focus_areas = []
    
    for dimension, info in mbti_dimensions.items():
        analysis = generate_dimension_analysis(dimension, info)
        info["analysis"] = analysis
        
        # Identify dimensions that might need further assessment
        if info["confidence"] < confidence_threshold:
            focus_areas.append(dimension)
    
    return {
        "mbti": {
            "type": mbti_type,
            "e_i": mbti_dimensions["e_i"],
            "s_n": mbti_dimensions["s_n"], 
            "t_f": mbti_dimensions["t_f"],
            "j_p": mbti_dimensions["j_p"]
        },
        "focus_areas": focus_areas,
        "confidence_overall": calculate_overall_confidence(mbti_dimensions)
    }


def calculate_mbti_dimensions(responses: list) -> Dict[str, Dict[str, Any]]:
    """Calculate MBTI dimensions based on responses."""
    # This is a simplified example - real implementation would use validated scoring algorithms
    # For this example, we'll create some representative scores
    return {
        "e_i": {  # Extraversion-Introversion
            "score": 0.35,
            "confidence": 0.82
        },
        "s_n": {  # Sensing-Intuition
            "score": 0.72,
            "confidence": 0.78
        },
        "t_f": {  # Thinking-Feeling
            "score": 0.45,
            "confidence": 0.75
        },
        "j_p": {  # Judging-Perceiving
            "score": 0.68,
            "confidence": 0.80
        }
    }


def determine_mbti_type(mbti_dimensions: Dict[str, Dict[str, Any]]) -> str:
    """Determine MBTI type based on dimension scores."""
    e_i = "I" if mbti_dimensions["e_i"]["score"] < 0.5 else "E"
    s_n = "N" if mbti_dimensions["s_n"]["score"] > 0.5 else "S"
    t_f = "F" if mbti_dimensions["t_f"]["score"] > 0.5 else "T"
    j_p = "J" if mbti_dimensions["j_p"]["score"] > 0.5 else "P"
    
    return f"{e_i}{s_n}{t_f}{j_p}"


def generate_dimension_analysis(dimension: str, info: Dict[str, Any]) -> str:
    """Generate text analysis for a specific MBTI dimension."""
    score = info["score"]
    
    if dimension == "e_i":  # Extraversion-Introversion
        if score > 0.6:
            return f"Extraversion preference (score: {score:.2f}). This indicates focus on external world, people, and activities. The individual likely gains energy from social interaction."
        elif score < 0.4:
            return f"Introversion preference (score: {score:.2f}). This indicates focus on internal world of ideas and concepts. The individual likely gains energy from solitary reflection."
        else:
            return f"Balanced orientation (score: {score:.2f}). The individual shows both extraverted and introverted tendencies depending on the situation."
    
    elif dimension == "s_n":  # Sensing-Intuition
        if score > 0.6:
            return f"Intuition preference (score: {score:.2f}). This indicates focus on possibilities, patterns, and abstract concepts. The individual likely focuses on the big picture."
        elif score < 0.4:
            return f"Sensing preference (score: {score:.2f}). This indicates focus on concrete facts and details. The individual likely focuses on the present moment and specific information."
        else:
            return f"Balanced information processing (score: {score:.2f}). The individual uses both sensing and intuitive approaches depending on the context."
    
    elif dimension == "t_f":  # Thinking-Feeling
        if score > 0.6:
            return f"Feeling preference (score: {score:.2f}). This indicates decision-making based on personal values and consideration of others. The individual likely prioritizes harmony."
        elif score < 0.4:
            return f"Thinking preference (score: {score:.2f}). This indicates decision-making based on logical analysis and objective criteria. The individual likely prioritizes consistency."
        else:
            return f"Balanced decision-making (score: {score:.2f}). The individual considers both logical analysis and personal values in decision-making."
    
    elif dimension == "j_p":  # Judging-Perceiving
        if score > 0.6:
            return f"Judging preference (score: {score:.2f}). This indicates preference for structure, planning, and organization. The individual likely prefers closure and decision-making."
        elif score < 0.4:
            return f"Perceiving preference (score: {score:.2f}). This indicates preference for flexibility, spontaneity, and adaptation. The individual likely prefers keeping options open."
        else:
            return f"Balanced lifestyle (score: {score:.2f}). The individual adapts their approach based on the situation, sometimes preferring structure and sometimes flexibility."
    
    return f"Analysis for {dimension} dimension with score {score:.2f}."


def calculate_overall_confidence(mbti_dimensions: Dict[str, Dict[str, Any]]) -> float:
    """Calculate overall confidence from individual dimension confidences."""
    confidences = [info["confidence"] for info in mbti_dimensions.values()]
    return sum(confidences) / len(confidences) if confidences else 0.0


def main():
    parser = argparse.ArgumentParser(description='Analyze MBTI personality type')
    parser.add_argument('--input', type=str, required=True, help='Path to input assessment results')
    parser.add_argument('--confidence-threshold', type=float, default=0.7, 
                       help='Confidence threshold for recommendations')
    
    args = parser.parse_args()
    
    try:
        result = analyze_mbti(
            input_file=args.input,
            confidence_threshold=args.confidence_threshold
        )
        print("MBTI analysis completed successfully!")
        print(f"Input file: {args.input}")
        print(f"Determined type: {result['mbti']['type']}")
    except Exception as e:
        print(f"Error during MBTI analysis: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())