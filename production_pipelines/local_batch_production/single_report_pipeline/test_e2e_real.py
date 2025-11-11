"""
End-to-end test for the complete single_report_pipeline with real Ollama integration
"""
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from segmentation import segment_report
from scoring import score_segment
from analysis import aggregate_scores, detect_discrepancy, calculate_big_five, generate_report


def test_complete_pipeline_with_real_ollama():
    """Test the complete pipeline with real Ollama calls"""
    print("Testing complete pipeline with real Ollama integration...")
    
    # Step 1: Create a sample report
    sample_report = """
    Question 1: How do you handle stress?
    Answer: I usually take a walk or meditate when I feel stressed.
    Criteria: Stress management techniques
    
    Question 2: What are your social habits?
    Answer: I enjoy spending time with friends on weekends.
    Criteria: Social interaction patterns
    
    Question 3: How do you approach problems?
    Answer: I analyze the situation and try different solutions.
    Criteria: Problem-solving approach
    """
    
    print("Step 1: Segmenting report...")
    segments = segment_report(sample_report)
    print(f"Found {len(segments)} segments")
    
    # Step 2: Score each segment using real Ollama calls
    print("Step 2: Scoring segments with real Ollama calls...")
    scores = []
    for i, segment in enumerate(segments):
        print(f"  Scoring segment {i+1}...")
        score = score_segment(segment, "Evaluate on a scale of 1-10", model='gemma:2b')
        scores.append(score)
        print(f"    Score: {score}")
    
    print(f"Step 3: Calculated scores: {scores}")
    
    # Step 4: Aggregate scores
    aggregated_score = aggregate_scores(scores)
    print(f"Step 4: Aggregated score (median): {aggregated_score}")
    
    # Step 5: Detect discrepancy (if we had more scores)
    discrepancy = detect_discrepancy(scores)
    print(f"Step 5: Discrepancy detected: {discrepancy}")
    
    # Step 6: Calculate Big Five (using our scores as example)
    # For a real implementation, we'd need more scores mapped to Big Five traits
    trait_mapping = {i: ['O', 'C', 'E', 'A', 'N'][i % 5] for i in range(len(scores))}
    if len(scores) >= 5:  # Need at least 5 scores for all 5 traits
        big_five = calculate_big_five(scores[:5], trait_mapping)
        print(f"Step 6: Big Five scores: {big_five}")
    else:
        # Pad with additional scores for demonstration
        extended_scores = scores + [5.0, 6.0, 7.0, 8.0, 9.0]  # Extend to have 5+ scores
        trait_mapping = {i: ['O', 'C', 'E', 'A', 'N'][i % 5] for i in range(len(extended_scores))}
        big_five = calculate_big_five(extended_scores, trait_mapping)
        print(f"Step 6: Big Five scores: {big_five}")
    
    # Step 7: Generate final report
    metadata = {
        'report_id': 'TEST001',
        'subject_id': 'SUBJ001',
        'date': '2023-12-07'
    }
    
    analysis_results = {
        'big_five': big_five,
        'aggregate_score': aggregated_score,
        'discrepancy_detected': discrepancy
    }
    
    report = generate_report(metadata, analysis_results)
    print("Step 7: Generated final report:")
    print(report)
    
    return True


if __name__ == "__main__":
    test_complete_pipeline_with_real_ollama()
    print("\nEnd-to-end test completed successfully!")