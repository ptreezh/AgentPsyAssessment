"""
Stress recommendation generator for AgentPsyAssessment
This script generates targeted stress testing recommendations based on personality profiles.
"""

import json
import argparse
import os
from typing import Dict, Any, List

def generate_stress_recommendations(input_file: str, confidence_threshold: float = 0.7) -> Dict[str, Any]:
    """
    Generate stress testing recommendations based on personality profile.
    
    Args:
        input_file: Path to assessment results file
        confidence_threshold: Confidence threshold for recommendations
    
    Returns:
        Dictionary containing stress testing recommendations
    """
    # Load the assessment results
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file does not exist: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        assessment_data = json.load(f)
    
    # Generate stress recommendations
    result = run_stress_recommendation_generation(assessment_data, confidence_threshold)
    
    # Add metadata to the result
    result.update({
        "input_assessment_id": assessment_data.get("id", "unknown"),
        "analysis_type": "stress_recommendations",
        "confidence_threshold": confidence_threshold
    })
    
    # Save results to file
    output_file = f"results/stress_recommendations_{os.path.basename(input_file)}"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Stress recommendations saved to: {output_file}")
    return result


def run_stress_recommendation_generation(assessment_data: Dict[str, Any], confidence_threshold: float) -> Dict[str, Any]:
    """Generate stress testing recommendations based on personality profile."""
    print("Generating stress testing recommendations...")
    
    # Extract personality data
    big_five = assessment_data.get("big_five", {})
    mbti = assessment_data.get("mbti", {})
    
    # Generate recommendations
    recommendations = create_stress_recommendations(big_five, mbti, confidence_threshold)
    
    return {
        "stress_recommendations": recommendations,
        "confidence_overall": calculate_recommendation_confidence(recommendations)
    }


def create_stress_recommendations(big_five: Dict[str, Any], mbti: Dict[str, Any], confidence_threshold: float) -> List[Dict[str, Any]]:
    """Create targeted stress testing recommendations based on personality profile."""
    recommendations = []
    
    # Generate recommendations based on Big Five scores
    if big_five:
        recommendations.extend(generate_bigfive_recommendations(big_five, confidence_threshold))
    
    # Generate recommendations based on MBTI type
    if mbti:
        recommendations.extend(generate_mbti_recommendations(mbti, confidence_threshold))
    
    # Generate general recommendations
    recommendations.extend(generate_general_recommendations(big_five, mbti, confidence_threshold))
    
    return recommendations


def generate_bigfive_recommendations(big_five: Dict[str, Any], confidence_threshold: float) -> List[Dict[str, Any]]:
    """Generate stress recommendations based on Big Five scores."""
    recommendations = []
    
    # Neuroticism-based recommendations
    neuroticism = big_five.get("neuroticism", {})
    if neuroticism:
        raw_score = neuroticism.get("raw_score", 0)
        percentile = neuroticism.get("percentile", 0)
        confidence = neuroticism.get("confidence", 0.5)
        
        if raw_score > 60 and confidence >= confidence_threshold:
            recommendations.append({
                "dimension": "neuroticism",
                "risk_level": "high",
                "recommendation": "Suggested high-stress resilience training focusing on emotion regulation, mindfulness, and cognitive restructuring techniques.",
                "confidence": confidence,
                "basis": f"High neuroticism score ({raw_score}) indicates greater sensitivity to stress and emotional volatility."
            })
        elif raw_score > 40 and confidence >= confidence_threshold:
            recommendations.append({
                "dimension": "neuroticism",
                "risk_level": "medium", 
                "recommendation": "Suggested moderate stress exposure exercises with emphasis on building coping strategies and resilience.",
                "confidence": confidence,
                "basis": f"Medium neuroticism score ({raw_score}) indicates moderate stress sensitivity."
            })
        elif confidence >= confidence_threshold:
            recommendations.append({
                "dimension": "neuroticism",
                "risk_level": "low",
                "recommendation": "Suggested varied stress scenarios to assess robustness under different conditions.",
                "confidence": confidence,
                "basis": f"Low neuroticism score ({raw_score}) indicates good emotional stability under stress."
            })
    
    # Extraversion-based recommendations
    extraversion = big_five.get("extraversion", {})
    if extraversion:
        raw_score = extraversion.get("raw_score", 0)
        confidence = extraversion.get("confidence", 0.5)
        
        if raw_score < 40 and confidence >= confidence_threshold:
            recommendations.append({
                "dimension": "extraversion",
                "risk_level": "medium",
                "recommendation": "Suggested social stress testing in group environments to assess performance under social pressure.",
                "confidence": confidence,
                "basis": f"Lower extraversion score ({raw_score}) may indicate sensitivity to social stress."
            })
        elif raw_score > 60 and confidence >= confidence_threshold:
            recommendations.append({
                "dimension": "extraversion",
                "risk_level": "low",
                "recommendation": "Suggested individual-focused stress testing to assess performance without social elements.",
                "confidence": confidence,
                "basis": f"High extraversion score ({raw_score}) suggests resilience in social stress scenarios."
            })
    
    # Conscientiousness-based recommendations
    conscientiousness = big_five.get("conscientiousness", {})
    if conscientiousness:
        raw_score = conscientiousness.get("raw_score", 0)
        confidence = conscientiousness.get("confidence", 0.5)
        
        if raw_score < 40 and confidence >= confidence_threshold:
            recommendations.append({
                "dimension": "conscientiousness",
                "risk_level": "medium",
                "recommendation": "Suggested structure-free stress testing to assess performance in unstructured environments.",
                "confidence": confidence,
                "basis": f"Lower conscientiousness score ({raw_score}) may indicate challenges with unstructured stress."
            })
        elif raw_score > 60 and confidence >= confidence_threshold:
            recommendations.append({
                "dimension": "conscientiousness",
                "risk_level": "low",
                "recommendation": "Suggested deadline-based stress testing to assess performance under time pressure.",
                "confidence": confidence,
                "basis": f"High conscientiousness score ({raw_score}) suggests good performance under structured stress."
            })
    
    return recommendations


def generate_mbti_recommendations(mbti: Dict[str, Any], confidence_threshold: float) -> List[Dict[str, Any]]:
    """Generate stress recommendations based on MBTI type."""
    recommendations = []
    
    mbti_type = mbti.get("type", "")
    if not mbti_type:
        return recommendations
    
    # Introversion-Extraversion recommendations
    e_i = mbti.get("e_i", {})
    e_i_score = e_i.get("score", 0.5)
    e_i_confidence = e_i.get("confidence", 0.5)
    
    if e_i_score < 0.4 and e_i_confidence >= confidence_threshold:
        recommendations.append({
            "dimension": "extraversion_introversion",
            "risk_level": "medium",
            "recommendation": "Suggested social stress testing in large group environments to assess performance under social pressure.",
            "confidence": e_i_confidence,
            "basis": f"Introversion preference (score: {e_i_score:.2f}) may indicate sensitivity to social stress."
        })
    elif e_i_score > 0.6 and e_i_confidence >= confidence_threshold:
        recommendations.append({
            "dimension": "extraversion_introversion",
            "risk_level": "low",
            "recommendation": "Suggested varied social stress scenarios to assess adaptability across different social contexts.",
            "confidence": e_i_confidence,
            "basis": f"Extraversion preference (score: {e_i_score:.2f}) suggests good resilience in social stress scenarios."
        })
    
    # Sensing-Intuition recommendations
    s_n = mbti.get("s_n", {})
    s_n_score = s_n.get("score", 0.5)
    s_n_confidence = s_n.get("confidence", 0.5)
    
    if s_n_score > 0.6 and s_n_confidence >= confidence_threshold:
        recommendations.append({
            "dimension": "sensing_intuition",
            "risk_level": "medium",
            "recommendation": "Suggested ambiguity-based stress testing to assess comfort with unclear or incomplete information.",
            "confidence": s_n_confidence,
            "basis": f"Intuition preference (score: {s_n_score:.2f}) may indicate challenges with ambiguous stress."
        })
    elif s_n_score < 0.4 and s_n_confidence >= confidence_threshold:
        recommendations.append({
            "dimension": "sensing_intuition",
            "risk_level": "low",
            "recommendation": "Suggested detail-focused stress testing to assess performance with complex concrete information.",
            "confidence": s_n_confidence,
            "basis": f"Sensing preference (score: {s_n_score:.2f}) suggests good handling of concrete stress."
        })
    
    # Thinking-Feeling recommendations
    t_f = mbti.get("t_f", {})
    t_f_score = t_f.get("score", 0.5)
    t_f_confidence = t_f.get("confidence", 0.5)
    
    if t_f_score > 0.6 and t_f_confidence >= confidence_threshold:
        recommendations.append({
            "dimension": "thinking_feeling",
            "risk_level": "medium",
            "recommendation": "Suggested interpersonal conflict stress testing to assess comfort with criticism and disagreement.",
            "confidence": t_f_confidence,
            "basis": f"Feeling preference (score: {t_f_score:.2f}) may indicate sensitivity to interpersonal stress."
        })
    elif t_f_score < 0.4 and t_f_confidence >= confidence_threshold:
        recommendations.append({
            "dimension": "thinking_feeling",
            "risk_level": "low",
            "recommendation": "Suggested critique-based stress testing to assess performance under analytical pressure.",
            "confidence": t_f_confidence,
            "basis": f"Thinking preference (score: {t_f_score:.2f}) suggests good handling of analytical stress."
        })
    
    # Judging-Perceiving recommendations
    j_p = mbti.get("j_p", {})
    j_p_score = j_p.get("score", 0.5)
    j_p_confidence = j_p.get("confidence", 0.5)
    
    if j_p_score > 0.6 and j_p_confidence >= confidence_threshold:
        recommendations.append({
            "dimension": "judging_perceiving",
            "risk_level": "medium",
            "recommendation": "Suggested uncertainty-based stress testing to assess comfort with changing plans and unexpected events.",
            "confidence": j_p_confidence,
            "basis": f"Judging preference (score: {j_p_score:.2f}) may indicate challenges with unpredictable stress."
        })
    elif j_p_score < 0.4 and j_p_confidence >= confidence_threshold:
        recommendations.append({
            "dimension": "judging_perceiving",
            "risk_level": "low",
            "recommendation": "Suggested adaptive stress testing to assess performance in fluid environments.",
            "confidence": j_p_confidence,
            "basis": f"Perceiving preference (score: {j_p_score:.2f}) suggests good adaptability to stress."
        })
    
    return recommendations


def generate_general_recommendations(big_five: Dict[str, Any], mbti: Dict[str, Any], confidence_threshold: float) -> List[Dict[str, Any]]:
    """Generate general stress recommendations not tied to specific dimensions."""
    recommendations = []
    
    # General recommendation for comprehensive stress testing
    recommendations.append({
        "dimension": "general",
        "risk_level": "medium",
        "recommendation": "Suggested comprehensive stress battery including time pressure, social pressure, ambiguity, and physical discomfort scenarios.",
        "confidence": 0.9,
        "basis": "Recommended baseline for all personality types to establish comprehensive stress profile."
    })
    
    # Recommendation for follow-up testing
    recommendations.append({
        "dimension": "follow_up",
        "risk_level": "low",
        "recommendation": "Suggested targeted follow-up testing focusing on identified stress sensitivities after initial assessment.",
        "confidence": 0.95,
        "basis": "Recommended refinement approach based on initial stress testing results."
    })
    
    return recommendations


def calculate_recommendation_confidence(recommendations: List[Dict[str, Any]]) -> float:
    """Calculate overall confidence from individual recommendation confidences."""
    if not recommendations:
        return 0.0
    
    confidences = [rec["confidence"] for rec in recommendations if "confidence" in rec]
    return sum(confidences) / len(confidences) if confidences else 0.0


def main():
    parser = argparse.ArgumentParser(description='Generate stress testing recommendations')
    parser.add_argument('--input', type=str, required=True, help='Path to input assessment results')
    parser.add_argument('--confidence-threshold', type=float, default=0.7, 
                       help='Confidence threshold for recommendations')
    
    args = parser.parse_args()
    
    try:
        result = generate_stress_recommendations(
            input_file=args.input,
            confidence_threshold=args.confidence_threshold
        )
        print("Stress recommendations generated successfully!")
        print(f"Input file: {args.input}")
        print(f"Generated {len(result.get('stress_recommendations', []))} recommendations")
    except Exception as e:
        print(f"Error generating stress recommendations: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())