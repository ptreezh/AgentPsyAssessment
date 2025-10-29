"""
Big Five analysis script for AgentPsyAssessment
This script provides functions to analyze assessment results specifically for Big Five personality dimensions.
"""

import json
import argparse
import os
from typing import Dict, Any

def analyze_big5(input_file: str, confidence_threshold: float = 0.7) -> Dict[str, Any]:
    """
    Analyze assessment results for Big Five personality dimensions.
    
    Args:
        input_file: Path to assessment results file
        confidence_threshold: Confidence threshold for recommendations
    
    Returns:
        Dictionary containing Big Five analysis results
    """
    # Load the assessment results
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file does not exist: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        assessment_data = json.load(f)
    
    # Perform Big Five analysis
    result = run_big5_analysis(assessment_data, confidence_threshold)
    
    # Add metadata to the result
    result.update({
        "input_assessment_id": assessment_data.get("id", "unknown"),
        "analysis_type": "bigfive",
        "confidence_threshold": confidence_threshold
    })
    
    # Save results to file
    output_file = f"results/bigfive_analysis_{os.path.basename(input_file)}"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Big Five analysis results saved to: {output_file}")
    return result


def run_big5_analysis(assessment_data: Dict[str, Any], confidence_threshold: float) -> Dict[str, Any]:
    """Perform detailed Big Five personality analysis."""
    print("Performing Big Five analysis...")
    
    # This is a placeholder implementation - in a real system, this would contain
    # actual analysis logic for Big Five dimensions
    # Extract relevant data from assessment
    responses = assessment_data.get("responses", [])
    
    # Calculate Big Five scores (simplified example)
    bigfive_scores = calculate_bigfive_scores(responses)
    
    # Generate analysis for each dimension
    bigfive_analysis = {}
    focus_areas = []
    
    for dimension, score_info in bigfive_scores.items():
        analysis = generate_dimension_analysis(dimension, score_info)
        score_info["analysis"] = analysis
        
        # Identify dimensions that might need further assessment
        if score_info["confidence"] < confidence_threshold:
            focus_areas.append(dimension)
    
    return {
        "big_five": bigfive_scores,
        "focus_areas": focus_areas,
        "confidence_overall": calculate_overall_confidence(bigfive_scores)
    }


def calculate_bigfive_scores(responses: list) -> Dict[str, Dict[str, Any]]:
    """Calculate Big Five scores based on responses."""
    # This is a simplified example - real implementation would use validated scoring algorithms
    # For this example, we'll create some representative scores
    return {
        "openness": {
            "raw_score": 65,
            "percentile": 0.78,
            "confidence": 0.85
        },
        "conscientiousness": {
            "raw_score": 58, 
            "percentile": 0.65,
            "confidence": 0.82
        },
        "extraversion": {
            "raw_score": 42,
            "percentile": 0.38,
            "confidence": 0.79
        },
        "agreeableness": {
            "raw_score": 71,
            "percentile": 0.84,
            "confidence": 0.88
        },
        "neuroticism": {
            "raw_score": 35,
            "percentile": 0.22,
            "confidence": 0.75
        }
    }


def generate_dimension_analysis(dimension: str, score_info: Dict[str, Any]) -> str:
    """Generate text analysis for a specific Big Five dimension."""
    raw_score = score_info["raw_score"]
    percentile = score_info["percentile"]
    
    if dimension == "openness":
        if raw_score > 60:
            return f"High openness to experience (score: {raw_score}). This suggests a preference for novelty, creativity, and intellectual exploration. The individual likely enjoys new experiences and abstract thinking."
        elif raw_score > 40:
            return f"Moderate openness to experience (score: {raw_score}). The individual shows balanced interest in new experiences and traditional approaches."
        else:
            return f"Lower openness to experience (score: {raw_score}). This suggests a preference for conventional, traditional activities and familiar routines."
    
    elif dimension == "conscientiousness":
        if raw_score > 60:
            return f"High conscientiousness (score: {raw_score}). This indicates strong self-discipline, organization, and goal-directed behavior. The individual likely plans carefully and follows through on commitments."
        elif raw_score > 40:
            return f"Moderate conscientiousness (score: {raw_score}). The individual shows balanced planning and organizational behavior."
        else:
            return f"Lower conscientiousness (score: {raw_score}). This suggests a more spontaneous and flexible approach with less emphasis on detailed planning."
    
    elif dimension == "extraversion":
        if raw_score > 60:
            return f"High extraversion (score: {raw_score}). This indicates sociability, assertiveness, and high energy in social situations. The individual likely enjoys group activities and external stimulation."
        elif raw_score > 40:
            return f"Moderate extraversion (score: {raw_score}). The individual shows balanced social behavior with both introverted and extraverted tendencies."
        else:
            return f"Lower extraversion (score: {raw_score}). This suggests a preference for solitary activities and internal reflection over external stimulation."
    
    elif dimension == "agreeableness":
        if raw_score > 60:
            return f"High agreeableness (score: {raw_score}). This indicates trust, altruism, and cooperation. The individual likely values harmony and is considerate of others."
        elif raw_score > 40:
            return f"Moderate agreeableness (score: {raw_score}). The individual shows balanced cooperation and self-interest."
        else:
            return f"Lower agreeableness (score: {raw_score}). This suggests a more competitive and critical approach, with emphasis on self-interest."
    
    elif dimension == "neuroticism":
        if raw_score > 60:
            return f"Higher neuroticism (score: {raw_score}). This indicates emotional instability and tendency toward psychological stress. The individual may experience anxiety, mood swings, or sadness more frequently."
        elif raw_score > 40:
            return f"Moderate neuroticism (score: {raw_score}). The individual shows balanced emotional responses."
        else:
            return f"Lower neuroticism (score: {raw_score}). This suggests emotional stability and resilience to stress. The individual likely remains calm under pressure."
    
    return f"Analysis for {dimension} dimension with score {raw_score}."


def calculate_overall_confidence(bigfive_scores: Dict[str, Dict[str, Any]]) -> float:
    """Calculate overall confidence from individual dimension confidences."""
    confidences = [score_info["confidence"] for score_info in bigfive_scores.values()]
    return sum(confidences) / len(confidences) if confidences else 0.0


def main():
    parser = argparse.ArgumentParser(description='Analyze Big Five personality dimensions')
    parser.add_argument('--input', type=str, required=True, help='Path to input assessment results')
    parser.add_argument('--confidence-threshold', type=float, default=0.7, 
                       help='Confidence threshold for recommendations')
    
    args = parser.parse_args()
    
    try:
        result = analyze_big5(
            input_file=args.input,
            confidence_threshold=args.confidence_threshold
        )
        print("Big Five analysis completed successfully!")
        print(f"Input file: {args.input}")
    except Exception as e:
        print(f"Error during Big Five analysis: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())