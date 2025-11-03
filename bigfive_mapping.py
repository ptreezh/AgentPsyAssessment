"""
Mapping functions from Big Five personality traits to MBTI and Belbin team roles.
Based on research and theoretical correlations between personality models.
"""

from typing import Dict, List, Union
import math

def bigfive_to_mbti(bigfive_scores: Dict[str, float]) -> str:
    """
    Map Big Five personality scores to MBTI type.
    
    Args:
        bigfive_scores: Dictionary with Big Five dimensions as keys and scores (1-5 scale)
        
    Returns:
        4-letter MBTI type string
    """
    if not bigfive_scores or len(bigfive_scores) < 5:
        raise ValueError("Big Five scores must contain all five dimensions: Extraversion, Agreeableness, Conscientiousness, Neuroticism, Openness")
    
    required_keys = ['Extraversion', 'Agreeableness', 'Conscientiousness', 'Neuroticism', 'Openness']
    for key in required_keys:
        if key not in bigfive_scores:
            raise ValueError(f"Missing required dimension: {key}")
        if not 1 <= bigfive_scores[key] <= 5:
            raise ValueError(f"Score for {key} must be between 1 and 5, got: {bigfive_scores[key]}")
    
    extraversion = bigfive_scores['Extraversion']
    agreeableness = bigfive_scores['Agreeableness']
    conscientiousness = bigfive_scores['Conscientiousness']
    neuroticism = bigfive_scores['Neuroticism']
    openness = bigfive_scores['Openness']
    
    # Determine E/I (Extraversion/Introversion)
    ei = 'E' if extraversion >= 3.0 else 'I'
    
    # Determine S/N (Sensing/Intuitive) based on Openness to Experience
    # High openness tends to correlate with intuition
    sn = 'N' if openness >= 3.0 else 'S'
    
    # Determine T/F (Thinking/Feeling) based on Agreeableness
    # Lower agreeableness (more direct/critical) correlates with Thinking
    # Higher agreeableness (more empathetic/cooperative) correlates with Feeling
    tf = 'F' if agreeableness >= 3.0 else 'T'
    
    # Determine J/P (Judging/Perceiving) based on Conscientiousness
    # High conscientiousness tends to correlate with Judging
    # Low conscientiousness (more flexible/spontaneous) correlates with Perceiving
    jp = 'J' if conscientiousness >= 3.0 else 'P'
    
    return f"{ei}{sn}{tf}{jp}"


def bigfive_to_belbin(bigfive_scores: Dict[str, float], top_n: int = 3) -> List[str]:
    """
    Map Big Five personality scores to Belbin team roles.
    
    Args:
        bigfive_scores: Dictionary with Big Five dimensions as keys and scores (1-5 scale)
        top_n: Number of top matching roles to return (default: 3)
        
    Returns:
        List of top matching Belbin roles
    """
    if not bigfive_scores or len(bigfive_scores) < 5:
        raise ValueError("Big Five scores must contain all five dimensions: Extraversion, Agreeableness, Conscientiousness, Neuroticism, Openness")
    
    required_keys = ['Extraversion', 'Agreeableness', 'Conscientiousness', 'Neuroticism', 'Openness']
    for key in required_keys:
        if key not in bigfive_scores:
            raise ValueError(f"Missing required dimension: {key}")
        if not 1 <= bigfive_scores[key] <= 5:
            raise ValueError(f"Score for {key} must be between 1 and 5, got: {bigfive_scores[key]}")
    
    extraversion = bigfive_scores['Extraversion']
    agreeableness = bigfive_scores['Agreeableness']
    conscientiousness = bigfive_scores['Conscientiousness']
    neuroticism = bigfive_scores['Neuroticism']
    openness = bigfive_scores['Openness']
    
    # Calculate scores for each Belbin role based on correlations with Big Five
    belbin_scores = {}
    
    # Resource Investigator (RI): High extraversion, high openness
    belbin_scores['Resource Investigator'] = (extraversion * 0.6) + (openness * 0.4)
    
    # Teamworker (TW): High agreeableness, moderate extraversion
    belbin_scores['Teamworker'] = (agreeableness * 0.6) + (extraversion * 0.2) + (neuroticism * -0.2)
    
    # Co-ordinator (CO): High conscientiousness, high agreeableness, some extraversion
    belbin_scores['Co-ordinator'] = (conscientiousness * 0.4) + (agreeableness * 0.3) + (extraversion * 0.3)
    
    # Plant (PL): High openness, moderate extraversion
    belbin_scores['Plant'] = (openness * 0.7) + (extraversion * 0.1) + (agreeableness * -0.2)
    
    # Monitor Evaluator (ME): High openness, high conscientiousness, lower extraversion
    belbin_scores['Monitor Evaluator'] = (openness * 0.4) + (conscientiousness * 0.4) + (extraversion * -0.2)
    
    # Specialist (SP): High conscientiousness, high openness in specific area
    belbin_scores['Specialist'] = (conscientiousness * 0.6) + (openness * 0.4)
    
    # Implementer (IMP): High conscientiousness, moderate agreeableness
    belbin_scores['Implementer'] = (conscientiousness * 0.7) + (agreeableness * 0.2) + (extraversion * -0.1)
    
    # Completer Finisher (CF): High conscientiousness, high neuroticism (attention to detail)
    belbin_scores['Completer Finisher'] = (conscientiousness * 0.6) + (neuroticism * 0.4)
    
    # Shaper (SH): High extraversion, low neuroticism (resilience), moderate conscientiousness
    belbin_scores['Shaper'] = (extraversion * 0.4) + ((5 - neuroticism) * 0.4) + (conscientiousness * 0.2)
    
    # Sort roles by score and return the top N
    sorted_roles = sorted(belbin_scores.items(), key=lambda x: x[1], reverse=True)
    top_roles = [role for role, score in sorted_roles[:top_n]]
    
    return top_roles


def calculate_mbti_percentile_scores(bigfive_scores: Dict[str, float]) -> Dict[str, float]:
    """
    Calculate MBTI dimension percentile scores based on Big Five scores.
    
    Args:
        bigfive_scores: Dictionary with Big Five dimensions as keys and scores (1-5 scale)
        
    Returns:
        Dictionary with MBTI dimensions and their percentile scores (0-100)
    """
    if not bigfive_scores or len(bigfive_scores) < 5:
        raise ValueError("Big Five scores must contain all five dimensions")
    
    required_keys = ['Extraversion', 'Agreeableness', 'Conscientiousness', 'Neuroticism', 'Openness']
    for key in required_keys:
        if key not in bigfive_scores:
            raise ValueError(f"Missing required dimension: {key}")
        if not 1 <= bigfive_scores[key] <= 5:
            raise ValueError(f"Score for {key} must be between 1 and 5, got: {bigfive_scores[key]}")
    
    extraversion = bigfive_scores['Extraversion']
    agreeableness = bigfive_scores['Agreeableness']
    conscientiousness = bigfive_scores['Conscientiousness']
    neuroticism = bigfive_scores['Neuroticism']
    openness = bigfive_scores['Openness']
    
    # Convert 1-5 scale to percentiles (0-100)
    def score_to_percentile(score):
        return ((score - 1) / 4) * 100
    
    # E-I: Extraversion directly corresponds to E-I dimension
    ei_percentile = score_to_percentile(extraversion)
    
    # S-N: Based on Openness (higher openness = more intuitive)
    sn_percentile = score_to_percentile(openness)
    
    # T-F: Based on Agreeableness (lower agreeableness = more thinking-oriented)
    # Invert the scale for T-F so that low agreeableness = high thinking percentile
    tf_percentile = score_to_percentile(6 - agreeableness)  # 6 - agreeableness inverts the scale (1->5, 5->1)
    
    # J-P: Based on Conscientiousness (higher = more judging)
    jp_percentile = score_to_percentile(conscientiousness)
    
    return {
        'EI_percentile': ei_percentile,
        'SN_percentile': sn_percentile,
        'TF_percentile': tf_percentile,
        'JP_percentile': jp_percentile
    }


def calculate_belbin_percentile_scores(bigfive_scores: Dict[str, float]) -> Dict[str, Dict[str, float]]:
    """
    Calculate Belbin role percentile scores based on Big Five scores.
    
    Args:
        bigfive_scores: Dictionary with Big Five dimensions as keys and scores (1-5 scale)
        
    Returns:
        Dictionary with each Belbin role and its score (0-100 scale)
    """
    if not bigfive_scores or len(bigfive_scores) < 5:
        raise ValueError("Big Five scores must contain all five dimensions")
    
    required_keys = ['Extraversion', 'Agreeableness', 'Conscientiousness', 'Neuroticism', 'Openness']
    for key in required_keys:
        if key not in bigfive_scores:
            raise ValueError(f"Missing required dimension: {key}")
        if not 1 <= bigfive_scores[key] <= 5:
            raise ValueError(f"Score for {key} must be between 1 and 5, got: {bigfive_scores[key]}")
    
    extraversion = bigfive_scores['Extraversion']
    agreeableness = bigfive_scores['Agreeableness']
    conscientiousness = bigfive_scores['Conscientiousness']
    neuroticism = bigfive_scores['Neuroticism']
    openness = bigfive_scores['Openness']
    
    # Calculate raw scores for each role (based on correlations with Big Five)
    raw_scores = {}
    
    # Convert raw scores to percentiles (0-100)
    def normalize_score(score, min_val, max_val):
        return ((score - min_val) / (max_val - min_val)) * 100 if max_val > min_val else 50
    
    # Calculate raw scores
    raw_scores['Resource Investigator'] = (extraversion * 0.6) + (openness * 0.4)
    raw_scores['Teamworker'] = (agreeableness * 0.6) + (extraversion * 0.2) + (neuroticism * -0.2)
    raw_scores['Co-ordinator'] = (conscientiousness * 0.4) + (agreeableness * 0.3) + (extraversion * 0.3)
    raw_scores['Plant'] = (openness * 0.7) + (extraversion * 0.1) + (agreeableness * -0.2)
    raw_scores['Monitor Evaluator'] = (openness * 0.4) + (conscientiousness * 0.4) + (extraversion * -0.2)
    raw_scores['Specialist'] = (conscientiousness * 0.6) + (openness * 0.4)
    raw_scores['Implementer'] = (conscientiousness * 0.7) + (agreeableness * 0.2) + (extraversion * -0.1)
    raw_scores['Completer Finisher'] = (conscientiousness * 0.6) + (neuroticism * 0.4)
    raw_scores['Shaper'] = (extraversion * 0.4) + ((5 - neuroticism) * 0.4) + (conscientiousness * 0.2)
    
    # Normalize all scores to 0-100 range
    # Theoretical min/max based on the scoring formulas
    min_possible = min(raw_scores.values())
    max_possible = max(raw_scores.values())
    
    percentile_scores = {}
    for role, raw_score in raw_scores.items():
        percentile_scores[role] = normalize_score(raw_score, min_possible, max_possible)
    
    return percentile_scores


if __name__ == "__main__":
    # Example usage
    sample_scores = {
        'Extraversion': 4.0,
        'Agreeableness': 3.5,
        'Conscientiousness': 4.2,
        'Neuroticism': 2.1,
        'Openness': 4.0
    }
    
    mbti = bigfive_to_mbti(sample_scores)
    belbin_roles = bigfive_to_belbin(sample_scores)
    mbti_percentiles = calculate_mbti_percentile_scores(sample_scores)
    belbin_percentiles = calculate_belbin_percentile_scores(sample_scores)
    
    print(f"Big Five scores: {sample_scores}")
    print(f"MBTI type: {mbti}")
    print(f"Top Belbin roles: {belbin_roles}")
    print(f"MBTI percentiles: {mbti_percentiles}")
    print(f"Belbin percentiles: {belbin_percentiles}")