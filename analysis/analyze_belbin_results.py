"""
Belbin analysis script for AgentPsyAssessment
This script provides functions to analyze assessment results for Belbin team roles.
"""

import json
import argparse
import os
from typing import Dict, Any

def analyze_belbin(input_file: str, confidence_threshold: float = 0.7) -> Dict[str, Any]:
    """
    Analyze assessment results for Belbin team roles.
    
    Args:
        input_file: Path to assessment results file
        confidence_threshold: Confidence threshold for recommendations
    
    Returns:
        Dictionary containing Belbin analysis results
    """
    # Load the assessment results
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file does not exist: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        assessment_data = json.load(f)
    
    # Perform Belbin analysis
    result = run_belbin_analysis(assessment_data, confidence_threshold)
    
    # Add metadata to the result
    result.update({
        "input_assessment_id": assessment_data.get("id", "unknown"),
        "analysis_type": "belbin",
        "confidence_threshold": confidence_threshold
    })
    
    # Save results to file
    output_file = f"results/belbin_analysis_{os.path.basename(input_file)}"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Belbin analysis results saved to: {output_file}")
    return result


def run_belbin_analysis(assessment_data: Dict[str, Any], confidence_threshold: float) -> Dict[str, Any]:
    """Perform detailed Belbin team role analysis."""
    print("Performing Belbin analysis...")
    
    # This is a placeholder implementation - in a real system, this would contain
    # actual analysis logic for Belbin team roles
    # Extract relevant data from assessment
    responses = assessment_data.get("responses", [])
    
    # Calculate Belbin roles (simplified example)
    belbin_scores = calculate_belbin_scores(responses)
    
    # Generate analysis for each role
    belbin_analysis = {}
    focus_areas = []
    
    for role, score_info in belbin_scores.items():
        analysis = generate_role_analysis(role, score_info)
        score_info["analysis"] = analysis
        
        # Identify roles that might need further assessment
        if score_info["confidence"] < confidence_threshold:
            focus_areas.append(role)
    
    return {
        "belbin": belbin_scores,
        "focus_areas": focus_areas,
        "confidence_overall": calculate_overall_confidence(belbin_scores)
    }


def calculate_belbin_scores(responses: list) -> Dict[str, Dict[str, Any]]:
    """Calculate Belbin team role scores based on responses."""
    # This is a simplified example - real implementation would use validated scoring algorithms
    # For this example, we'll create some representative scores
    return {
        "coordinator": {
            "score": 0.78,
            "confidence": 0.85
        },
        "shaper": {
            "score": 0.62,
            "confidence": 0.78
        },
        "plant": {
            "score": 0.85,
            "confidence": 0.88
        },
        "resource_investigator": {
            "score": 0.71,
            "confidence": 0.82
        },
        "monitor_evaluator": {
            "score": 0.76,
            "confidence": 0.80
        },
        "implementer": {
            "score": 0.58,
            "confidence": 0.72
        },
        "completer_finisher": {
            "score": 0.69,
            "confidence": 0.75
        },
        "teamworker": {
            "score": 0.82,
            "confidence": 0.86
        },
        "specialist": {
            "score": 0.74,
            "confidence": 0.79
        }
    }


def generate_role_analysis(role: str, score_info: Dict[str, Any]) -> str:
    """Generate text analysis for a specific Belbin team role."""
    score = score_info["score"]
    
    if role == "coordinator":
        if score > 0.7:
            return f"Strong coordinator tendencies (score: {score:.2f}). Effective at clarifying goals, promoting decision-making, and delegating tasks. Natural chairperson abilities."
        elif score > 0.4:
            return f"Moderate coordinator tendencies (score: {score:.2f}). Shows some ability to clarify goals and promote decision-making when needed."
        else:
            return f"Lower coordinator tendencies (score: {score:.2f}). Less likely to take formal leadership roles or coordinate group activities."
    
    elif role == "shaper":
        if score > 0.7:
            return f"Strong shaper tendencies (score: {score:.2f}). Challenging, dynamic, and driven to overcome obstacles. Creates beneficial pressure for team performance."
        elif score > 0.4:
            return f"Moderate shaper tendencies (score: {score:.2f}). Shows some ability to challenge the team and overcome obstacles when needed."
        else:
            return f"Lower shaper tendencies (score: {score:.2f}). Less likely to challenge the team or create pressure for performance."
    
    elif role == "plant":
        if score > 0.7:
            return f"Strong plant tendencies (score: {score:.2f}). Creative, imaginative, and innovative. Provides original solutions to complex problems."
        elif score > 0.4:
            return f"Moderate plant tendencies (score: {score:.2f}). Shows some creative problem-solving ability in appropriate situations."
        else:
            return f"Lower plant tendencies (score: {score:.2f}). Less focused on generating creative solutions to problems."
    
    elif role == "resource_investigator":
        if score > 0.7:
            return f"Strong resource investigator tendencies (score: {score:.2f}). Outgoing, enthusiastic, and communicative. Explores opportunities and develops external contacts."
        elif score > 0.4:
            return f"Moderate resource investigator tendencies (score: {score:.2f}). Shows some ability to develop external contacts and explore opportunities."
        else:
            return f"Lower resource investigator tendencies (score: {score:.2f}). Less likely to explore opportunities or develop external contacts."
    
    elif role == "monitor_evaluator":
        if score > 0.7:
            return f"Strong monitor evaluator tendencies (score: {score:.2f}). Sober, strategic, and discerning. Evaluates proposals critically and judges alternatives objectively."
        elif score > 0.4:
            return f"Moderate monitor evaluator tendencies (score: {score:.2f}). Shows some ability to evaluate proposals critically when needed."
        else:
            return f"Lower monitor evaluator tendencies (score: {score:.2f}). Less focused on critical evaluation of proposals and alternatives."
    
    elif role == "implementer":
        if score > 0.7:
            return f"Strong implementer tendencies (score: {score:.2f}). Disciplined, efficient, and practical. Transforms decisions into practical actions efficiently."
        elif score > 0.4:
            return f"Moderate implementer tendencies (score: {score:.2f}). Shows some ability to implement plans and turn ideas into action."
        else:
            return f"Lower implementer tendencies (score: {score:.2f}). Less focused on implementing practical actions from decisions."
    
    elif role == "completer_finisher":
        if score > 0.7:
            return f"Strong completer finisher tendencies (score: {score:.2f}). Painstaking, conscientious, and concerned with detail. Ensures work is completed thoroughly."
        elif score > 0.4:
            return f"Moderate completer finisher tendencies (score: {score:.2f}). Shows attention to detail and follow-through when needed."
        else:
            return f"Lower completer finisher tendencies (score: {score:.2f}). Less focused on ensuring thorough completion of work."
    
    elif role == "teamworker":
        if score > 0.7:
            return f"Strong teamworker tendencies (score: {score:.2f}). Cooperative, mild, and perceptive of others' needs. Provides essential input at a human level."
        elif score > 0.4:
            return f"Moderate teamworker tendencies (score: {score:.2f}). Shows some ability to work cooperatively and support team members."
        else:
            return f"Lower teamworker tendencies (score: {score:.2f}). Less focused on supporting team members or maintaining harmony."
    
    elif role == "specialist":
        if score > 0.7:
            return f"Strong specialist tendencies (score: {score:.2f}). Self-starting, dedicated, and provides knowledge and skills in rare supply to the team."
        elif score > 0.4:
            return f"Moderate specialist tendencies (score: {score:.2f}). Shows some depth of knowledge in specific areas."
        else:
            return f"Lower specialist tendencies (score: {score:.2f}). Less likely to focus on developing deep expertise in a specific area."
    
    return f"Analysis for {role} role with score {score:.2f}."


def calculate_overall_confidence(belbin_scores: Dict[str, Dict[str, Any]]) -> float:
    """Calculate overall confidence from individual role confidences."""
    confidences = [score_info["confidence"] for score_info in belbin_scores.values()]
    return sum(confidences) / len(confidences) if confidences else 0.0


def main():
    parser = argparse.ArgumentParser(description='Analyze Belbin team roles')
    parser.add_argument('--input', type=str, required=True, help='Path to input assessment results')
    parser.add_argument('--confidence-threshold', type=float, default=0.7, 
                       help='Confidence threshold for recommendations')
    
    args = parser.parse_args()
    
    try:
        result = analyze_belbin(
            input_file=args.input,
            confidence_threshold=args.confidence_threshold
        )
        print("Belbin analysis completed successfully!")
        print(f"Input file: {args.input}")
    except Exception as e:
        print(f"Error during Belbin analysis: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())