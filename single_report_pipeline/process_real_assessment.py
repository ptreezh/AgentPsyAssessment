"""
Process real assessment reports through the single_report_pipeline
"""
import json
import sys
import os
import re

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.segmentation import segment_report
from src.scoring import score_segment
from src.analysis import calculate_big_five, generate_report


def extract_questions_and_responses_from_assessment(assessment_file_path):
    """
    Extract questions and responses from the real JSON assessment file
    """
    with open(assessment_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract question-response pairs
    segments_data = []
    for item in data['assessment_results']:
        question_data = item['question_data']
        response = item['extracted_response']
        
        # Get the dimension and question concept
        dimension = question_data['dimension']  # e.g., 'Extraversion'
        concept = question_data['mapped_ipip_concept']  # e.g., 'E1: 我是团队活动的核心人物。'
        
        # Determine if this is a reverse-scored item
        is_reversed = 'Reversed' in concept or concept.startswith('N') or concept.startswith('E20') or concept.startswith('E25') or concept.startswith('E30') or concept.startswith('E35') or concept.startswith('E40') or concept.startswith('E45') or concept.startswith('E50') or concept.startswith('A21') or concept.startswith('A26') or concept.startswith('A31') or concept.startswith('A36') or concept.startswith('A41') or concept.startswith('A46') or concept.startswith('C22') or concept.startswith('C27') or concept.startswith('C32') or concept.startswith('C37') or concept.startswith('C42') or concept.startswith('C47') or concept.startswith('N6') or concept.startswith('N16') or concept.startswith('N26') or concept.startswith('N36') or concept.startswith('N46') or concept.startswith('O11') or concept.startswith('O16') or concept.startswith('O21') or concept.startswith('O26') or concept.startswith('O31') or concept.startswith('O36') or concept.startswith('O41') or concept.startswith('O46') or concept.startswith('E11') or concept.startswith('E16') or concept.startswith('E21') or concept.startswith('E26') or concept.startswith('E31') or concept.startswith('E36') or concept.startswith('E41') or concept.startswith('E46') or concept.startswith('A11') or concept.startswith('A16') or concept.startswith('A21') or concept.startswith('A26') or concept.startswith('A31') or concept.startswith('A36') or concept.startswith('A41') or concept.startswith('A46') or concept.startswith('C11') or concept.startswith('C16') or concept.startswith('C21') or concept.startswith('C26') or concept.startswith('C31') or concept.startswith('C36') or concept.startswith('C41') or concept.startswith('C46') or concept.startswith('N11') or concept.startswith('N16') or concept.startswith('N21') or concept.startswith('N26') or concept.startswith('N31') or concept.startswith('N36') or concept.startswith('N41') or concept.startswith('N46') or concept.startswith('O11') or concept.startswith('O16') or concept.startswith('O21') or concept.startswith('O26') or concept.startswith('O31') or concept.startswith('O36') or concept.startswith('O41') or concept.startswith('O46')
        
        # Determine the Big Five trait from the dimension
        trait_map = {
            'Extraversion': 'E',
            'Agreeableness': 'A', 
            'Conscientiousness': 'C',
            'Neuroticism': 'N', 
            'Openness to Experience': 'O'
        }
        trait = trait_map.get(dimension, 'U')  # U for unknown
        
        segments_data.append({
            'question': f"{concept}",
            'answer': response,
            'dimension': dimension,
            'trait': trait,
            'is_reversed': is_reversed
        })
    
    return segments_data


def process_real_assessment_report(assessment_file_path):
    """
    Process a real assessment report through the entire pipeline
    """
    print(f"Processing real assessment report: {assessment_file_path}")
    
    # Extract the questions and responses
    segments_data = extract_questions_and_responses_from_assessment(assessment_file_path)
    
    print(f"Extracted {len(segments_data)} question-response pairs")
    
    # Prepare the data for our pipeline
    # For this implementation, we'll use a simple text format that our pipeline can handle
    report_content = ""
    for i, seg in enumerate(segments_data):
        report_content += f"Question {i+1}: {seg['question']}\n"
        report_content += f"Answer: {seg['answer']}\n"
        report_content += f"Dimension: {seg['dimension']}\n\n"
    
    # Now process through the pipeline
    print("\nProcessing through single_report_pipeline...")
    
    # Step 1: Segment the report
    print("Step 1: Segmenting report...")
    segments = segment_report(report_content)
    print(f"Found {len(segments)} segments")
    
    # Step 2: Score each segment using Ollama
    print("Step 2: Scoring segments with real Ollama calls...")
    scores = []
    trait_mapping = {}
    reverse_scoring_map = {}
    
    for i, segment in enumerate(segments_data):
        print(f"  Scoring segment {i+1}/50: {segment['dimension']} - {segment['question'][:50]}...")
        
        # Score based on the evaluation rubric
        criteria = f"Evaluate this response based on the Big Five dimension: {segment['dimension']}. Score from 1-5 based on the evaluation rubric scale."
        try:
            score = score_segment(segment, criteria, model='deepseek-r1:8b')
            scores.append(score)
            trait_mapping[len(scores)-1] = segment['trait']
            
            if segment['is_reversed']:
                reverse_scoring_map[len(scores)-1] = True
                
            print(f"    Score: {score}")
        except Exception as e:
            print(f"    Error scoring segment: {e}")
            # Default score if Ollama fails
            scores.append(3.0)  # Neutral score
            trait_mapping[len(scores)-1] = segment['trait']
    
    # Step 3: Calculate Big Five scores
    print("Step 3: Calculating Big Five scores...")
    big_five_scores = calculate_big_five(
        scores, 
        trait_mapping, 
        reverse_scoring_map, 
        scale_range=(1, 5)
    )
    print(f"Big Five scores: {big_five_scores}")
    
    # Step 4: Generate final report
    print("Step 4: Generating final report...")
    
    # Calculate aggregate score
    aggregated_score = sum(scores) / len(scores) if scores else 0
    
    # Check for discrepancies
    discrepancy_detected = max(scores) - min(scores) > 2  # Simple discrepancy check
    
    # Prepare analysis results
    analysis_results = {
        'big_five': big_five_scores,
        'aggregate_score': aggregated_score,
        'discrepancy_detected': discrepancy_detected,
        'individual_scores': scores,
        'segment_count': len(segments_data)
    }
    
    # Generate the final report
    metadata = {
        'report_id': os.path.basename(assessment_file_path),
        'subject_id': 'REAL_ASSESSMENT',
        'date': '2025-11-02'
    }
    
    final_report = generate_report(metadata, analysis_results)
    print("\nFinal Report:")
    print("="*50)
    print(final_report)
    print("="*50)
    
    return {
        'segments': segments_data,
        'scores': scores,
        'trait_mapping': trait_mapping,
        'reverse_scoring_map': reverse_scoring_map,
        'big_five': big_five_scores,
        'final_report': final_report,
        'analysis_results': analysis_results
    }


if __name__ == "__main__":
    # Process one of the real assessment files
    assessment_path = r"D:\AIDevelop\portable_psyagent\results\readonly-original\asses_gemma3_latest_agent_big_five_50_complete2_def_e0_t0_0_09201.json"
    
    if os.path.exists(assessment_path):
        result = process_real_assessment_report(assessment_path)
        print(f"\nSuccessfully processed assessment report!")
        print(f"Big Five Results: {result['big_five']}")
    else:
        print(f"Assessment file not found: {assessment_path}")