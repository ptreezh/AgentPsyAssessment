"""
Main pipeline module that orchestrates the entire single report processing workflow.
"""
from .segmentation import segment_report
from .scoring import score_segment
from .analysis import aggregate_scores, detect_discrepancy, calculate_big_five, generate_report


def process_single_report(report_source, criteria="Evaluate on a scale of 1-5", model='deepseek-r1:8b'):
    """
    Process a single report through the entire pipeline.
    
    Args:
        report_source (str): Path to report file or report content string
        criteria (str): Criteria for scoring each segment
        model (str): Ollama model to use for scoring
        
    Returns:
        dict: Complete analysis results
    """
    # Step 1: Segment the report
    segments = segment_report(report_source)
    
    # Step 2: Score each segment
    scores = []
    for segment in segments:
        score = score_segment(segment, criteria, model=model)
        scores.append(score)
    
    # Step 3: Aggregate scores
    aggregated_score = aggregate_scores(scores)
    
    # Step 4: Detect discrepancies
    discrepancy_detected = detect_discrepancy(scores)
    
    # Step 5: Calculate Big Five (if we have enough segments mapped to traits)
    # For this example, we'll assume segments map to traits in round-robin fashion
    # In a real implementation, the trait_mapping would come from a proper questionnaire design
    trait_mapping = {i: ['O', 'C', 'E', 'A', 'N'][i % 5] for i in range(len(scores))}
    
    # For demonstration, let's say every 5th question starting from index 4 (the 5th question) is reverse scored
    # This simulates how some personality questionnaires have reverse-keyed items
    reverse_scoring_map = {i: True for i in range(4, len(scores), 5)}  # Every 5th question starting from index 4
    
    big_five_scores = calculate_big_five(scores, trait_mapping, reverse_scoring_map, scale_range=(1, 5))
    
    # Step 6: Generate final report
    metadata = {
        'report_id': 'AUTO_GEN',
        'subject_id': 'UNKNOWN',
        'date': '2023-12-07'
    }
    
    analysis_results = {
        'big_five': big_five_scores,
        'aggregate_score': aggregated_score,
        'discrepancy_detected': discrepancy_detected,
        'individual_scores': scores,
        'segment_count': len(segments)
    }
    
    final_report = generate_report(metadata, analysis_results)
    
    return {
        'segments': segments,
        'scores': scores,
        'aggregated_score': aggregated_score,
        'discrepancy_detected': discrepancy_detected,
        'big_five': big_five_scores,
        'final_report': final_report,
        'analysis_results': analysis_results
    }