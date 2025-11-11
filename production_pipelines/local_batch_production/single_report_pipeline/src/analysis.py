import statistics


def detect_discrepancy(scores, threshold=2.0):
    """
    Detects if there's a significant discrepancy in scores.
    
    Args:
        scores (list): List of numeric scores
        threshold (float): Threshold for what constitutes a discrepancy
        
    Returns:
        bool: True if discrepancy is detected, False otherwise
    """
    if len(scores) < 2:
        return False
    
    mean_score = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)
    
    # Check if the range exceeds the threshold
    if max_score - min_score >= threshold:
        return True
    
    # Check if any score is significantly different from the mean
    for score in scores:
        if abs(score - mean_score) >= threshold:
            return True
    
    return False


def aggregate_scores(scores):
    """
    Aggregates a list of scores into a final score.
    
    Args:
        scores (list): List of numeric scores
        
    Returns:
        float: The aggregated score
    """
    if not scores:
        return 0.0
    
    # Use median to reduce impact of outliers
    return statistics.median(scores)


def calculate_big_five(scores, trait_mapping, reverse_scoring_map=None, scale_range=(1, 5)):
    """
    Calculates Big Five personality trait scores from individual question scores.
    
    Args:
        scores (list): List of Likert scale ratings (e.g., 1-5) for individual questions
        trait_mapping (dict): Mapping from question index to Big Five trait ('O', 'C', 'E', 'A', 'N')
        reverse_scoring_map (dict): Optional mapping of question indices that need reverse scoring
                                   (e.g., {2: True, 5: True} means questions 2 and 5 are reverse scored)
        scale_range (tuple): The range of the Likert scale (min, max), default (1, 5)
        
    Returns:
        dict: Dictionary with trait names as keys and calculated scores as values
    """
    if reverse_scoring_map is None:
        reverse_scoring_map = {}
    
    min_scale, max_scale = scale_range
    
    # Group scores by trait, applying reverse scoring where needed
    trait_scores = {}
    for idx, original_score in enumerate(scores):
        trait = trait_mapping.get(idx)
        if trait is None:
            continue  # Skip questions that don't map to a trait
            
        # Apply reverse scoring if needed
        if idx in reverse_scoring_map:
            # Reverse the score: if scale is 1-5, 1 becomes 5, 2 becomes 4, etc.
            # Formula: (max + min) - original_score
            score = (max_scale + min_scale) - original_score
        else:
            score = original_score
            
        if trait not in trait_scores:
            trait_scores[trait] = []
        trait_scores[trait].append(score)
    
    # Calculate average for each trait
    trait_averages = {}
    for trait, scores_list in trait_scores.items():
        if scores_list:  # Only calculate if there are scores for this trait
            trait_averages[trait] = sum(scores_list) / len(scores_list)
        else:
            trait_averages[trait] = 0.0  # Or could be NaN, depending on requirements
    
    return trait_averages


def generate_report(metadata, analysis_results):
    """
    Generates a formatted final report from metadata and analysis results.
    
    Args:
        metadata (dict): Metadata including report_id, subject_id, date
        analysis_results (dict): Results from the analysis including big_five, aggregate_score, etc.
        
    Returns:
        str: Formatted report string
    """
    trait_names = {
        'O': 'Openness',
        'C': 'Conscientiousness', 
        'E': 'Extraversion',
        'A': 'Agreeableness',
        'N': 'Neuroticism'
    }
    
    report_parts = []
    report_parts.append("Personality Assessment Report")
    report_parts.append("=" * 30)
    report_parts.append(f"Report ID: {metadata.get('report_id', 'N/A')}")
    report_parts.append(f"Subject ID: {metadata.get('subject_id', 'N/A')}")
    report_parts.append(f"Date: {metadata.get('date', 'N/A')}")
    report_parts.append("")
    
    report_parts.append("Big Five Scores:")
    big_five = analysis_results.get('big_five', {})
    for trait_abbr, score in big_five.items():
        trait_name = trait_names.get(trait_abbr, trait_abbr)
        report_parts.append(f"{trait_name}: {score}")
    
    report_parts.append("")
    report_parts.append(f"Aggregate Score: {analysis_results.get('aggregate_score', 'N/A')}")
    
    discrepancy = analysis_results.get('discrepancy_detected', False)
    report_parts.append(f"Discrepancy Detected: {'Yes' if discrepancy else 'No'}")
    
    return "\n".join(report_parts)