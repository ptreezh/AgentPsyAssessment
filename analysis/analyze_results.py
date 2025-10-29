"""
Analysis starter script for AgentPsyAssessment
This script provides functions to analyze assessment results using various psychometric models.
"""

import json
import argparse
import os
from typing import Dict, Any, List, Optional

def run_analysis(input_file: str, analysis_type: str = "comprehensive", confidence_threshold: float = 0.7) -> Dict[str, Any]:
    """
    Analyze assessment results using specified analysis type.
    
    Args:
        input_file: Path to assessment results file
        analysis_type: Type of analysis to perform (bigfive, mbti, belbin, comprehensive)
        confidence_threshold: Confidence threshold for recommendations
    
    Returns:
        Dictionary containing analysis results
    """
    # Load the assessment results
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file does not exist: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        assessment_data = json.load(f)
    
    # Perform the requested analysis type
    if analysis_type == "bigfive":
        result = analyze_bigfive(assessment_data, confidence_threshold)
    elif analysis_type == "mbti":
        result = analyze_mbti(assessment_data, confidence_threshold)
    elif analysis_type == "belbin":
        result = analyze_belbin(assessment_data, confidence_threshold)
    elif analysis_type == "comprehensive":
        result = analyze_comprehensive(assessment_data, confidence_threshold)
    else:
        raise ValueError(f"Unknown analysis type: {analysis_type}")
    
    # Add metadata to the result
    result.update({
        "input_assessment_id": assessment_data.get("id", "unknown"),
        "analysis_type": analysis_type,
        "confidence_threshold": confidence_threshold
    })
    
    # Save results to file
    output_file = f"results/analysis_{analysis_type}_{os.path.basename(input_file)}"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Analysis results saved to: {output_file}")
    return result


def analyze_bigfive(assessment_data: Dict[str, Any], confidence_threshold: float) -> Dict[str, Any]:
    """Perform Big Five personality analysis."""
    # This is a placeholder implementation - in a real system, this would contain
    # actual analysis logic for Big Five dimensions
    print("Performing Big Five analysis...")
    
    # Extract relevant data from assessment
    responses = assessment_data.get("responses", [])
    
    # Calculate Big Five scores (simplified example)
    bigfive_scores = {
        "openness": {"raw_score": 0, "percentile": 0.0, "analysis": "Openness analysis", "confidence": 0.8},
        "conscientiousness": {"raw_score": 0, "percentile": 0.0, "analysis": "Conscientiousness analysis", "confidence": 0.8},
        "extraversion": {"raw_score": 0, "percentile": 0.0, "analysis": "Extraversion analysis", "confidence": 0.8},
        "agreeableness": {"raw_score": 0, "percentile": 0.0, "analysis": "Agreeableness analysis", "confidence": 0.8},
        "neuroticism": {"raw_score": 0, "percentile": 0.0, "analysis": "Neuroticism analysis", "confidence": 0.8}
    }
    
    return {
        "big_five": bigfive_scores,
        "focus_areas": ["neuroticism", "openness"]  # Areas that might need further assessment
    }


def analyze_mbti(assessment_data: Dict[str, Any], confidence_threshold: float) -> Dict[str, Any]:
    """Perform MBTI personality analysis."""
    print("Performing MBTI analysis...")
    
    # Calculate MBTI scores (simplified example)
    mbti_scores = {
        "type": "INFP",
        "e_i": {"score": 0.3, "confidence": 0.8, "analysis": "Introversion preference"},
        "s_n": {"score": 0.7, "confidence": 0.75, "analysis": "Intuition preference"},
        "t_f": {"score": 0.4, "confidence": 0.78, "analysis": "Feeling preference"},
        "j_p": {"score": 0.6, "confidence": 0.72, "analysis": "Perceiving preference"}
    }
    
    return {
        "mbti": mbti_scores,
        "focus_areas": ["t_f", "j_p"]
    }


def analyze_belbin(assessment_data: Dict[str, Any], confidence_threshold: float) -> Dict[str, Any]:
    """Perform Belbin team role analysis."""
    print("Performing Belbin analysis...")
    
    # Calculate Belbin scores (simplified example)
    belbin_scores = {
        "coordinator": {"score": 0.7, "confidence": 0.8, "analysis": "Strong coordination abilities"},
        "shaper": {"score": 0.5, "confidence": 0.75, "analysis": "Moderate drive to achieve results"},
        "plant": {"score": 0.8, "confidence": 0.85, "analysis": "High creative capacity"},
        "resource_investigator": {"score": 0.6, "confidence": 0.78, "analysis": "Good networker and explorer"},
        "monitor_evaluator": {"score": 0.7, "confidence": 0.82, "analysis": "Strong analytical skills"},
        "implementer": {"score": 0.4, "confidence": 0.7, "analysis": "Limited implementation focus"},
        "completer_finisher": {"score": 0.6, "confidence": 0.75, "analysis": "Attentive to detail"},
        "teamworker": {"score": 0.8, "confidence": 0.88, "analysis": "Strong collaboration skills"},
        "specialist": {"score": 0.7, "confidence": 0.8, "analysis": "Deep knowledge in specific areas"}
    }
    
    return {
        "belbin": belbin_scores,
        "focus_areas": ["implementer", "shaper"]
    }


def analyze_comprehensive(assessment_data: Dict[str, Any], confidence_threshold: float) -> Dict[str, Any]:
    """Perform comprehensive analysis combining multiple models."""
    print("Performing comprehensive analysis...")
    
    # Combine all analysis types
    bigfive_result = analyze_bigfive(assessment_data, confidence_threshold)
    mbti_result = analyze_mbti(assessment_data, confidence_threshold)
    belbin_result = analyze_belbin(assessment_data, confidence_threshold)
    
    # Generate stress recommendations based on profile
    stress_recommendations = generate_stress_recommendations(
        bigfive_result["big_five"],
        mbti_result["mbti"]
    )
    
    return {
        "big_five": bigfive_result["big_five"],
        "mbti": mbti_result["mbti"],
        "belbin": belbin_result["belbin"],
        "stress_recommendations": stress_recommendations,
        "confidence_overall": 0.8,
        "methodology": "Comprehensive psychometric analysis using multiple validated models",
        "notes": "Comprehensive analysis combining Big Five, MBTI, and Belbin models",
        "focus_areas": list(set(
            bigfive_result.get("focus_areas", []) +
            mbti_result.get("focus_areas", []) +
            belbin_result.get("focus_areas", [])
        ))
    }


def generate_stress_recommendations(bigfive_scores: Dict[str, Any], mbti_scores: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate stress testing recommendations based on personality profile."""
    recommendations = []
    
    # Example: Based on neuroticism score
    neuroticism_score = bigfive_scores.get("neuroticism", {}).get("raw_score", 0)
    if neuroticism_score > 50:
        recommendations.append({
            "dimension": "neuroticism",
            "risk_level": "high",
            "recommendation": "Suggested stress-reduction techniques for high neuroticism scores",
            "confidence": 0.85
        })
    elif neuroticism_score > 30:
        recommendations.append({
            "dimension": "neuroticism", 
            "risk_level": "medium",
            "recommendation": "Suggested stress-reduction techniques for medium neuroticism scores",
            "confidence": 0.80
        })
    
    # Example: Based on introversion score
    if mbti_scores.get("e_i", {}).get("score", 0.5) < 0.4:  # More introverted
        recommendations.append({
            "dimension": "extraversion_introversion",
            "risk_level": "medium",
            "recommendation": "Suggested social stress testing for introverted individuals",
            "confidence": 0.75
        })
    
    return recommendations


def main():
    parser = argparse.ArgumentParser(description='Analyze assessment results')
    parser.add_argument('--input', type=str, required=True, help='Path to input assessment results')
    parser.add_argument('--analysis-type', type=str, choices=['bigfive', 'mbti', 'belbin', 'comprehensive'], 
                       default='comprehensive', help='Type of analysis to perform')
    parser.add_argument('--confidence-threshold', type=float, default=0.7, 
                       help='Confidence threshold for recommendations')
    
    args = parser.parse_args()
    
    try:
        result = run_analysis(
            input_file=args.input,
            analysis_type=args.analysis_type,
            confidence_threshold=args.confidence_threshold
        )
        print("Analysis completed successfully!")
        print(f"Analysis type: {args.analysis_type}")
        print(f"Input file: {args.input}")
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())