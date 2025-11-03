import json
import os
import sys

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from src.scoring import score_segment
from src.analysis import calculate_big_five, generate_report

def extract_questions_and_responses_from_assessment(assessment_file_path):
    with open(assessment_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    segments_data = []
    for item in data['assessment_results']:
        question_data = item['question_data']
        response = item['extracted_response']
        
        dimension = question_data['dimension']
        concept = question_data['mapped_ipip_concept']
        
        # Check if item is reversed
        is_reversed = 'Reversed' in concept
        
        trait_map = {
            'Extraversion': 'E',
            'Agreeableness': 'A', 
            'Conscientiousness': 'C',
            'Neuroticism': 'N', 
            'Openness to Experience': 'O'
        }
        trait = trait_map.get(dimension, 'U')
        
        segments_data.append({
            'question': f'{concept}',
            'answer': response,
            'dimension': dimension,
            'trait': trait,
            'is_reversed': is_reversed
        })
    
    return segments_data

# Process a few more real assessment files
assessment_dir = r'D:\AIDevelop\portable_psyagent\results\readonly-original'
assessment_files = [
    'asses_qwen3_32b_agent_big_five_50_complete2_def_e0_t0_0_09281.json',
    'asses_llama3.1_70b_agent_big_five_50_complete2_def_e0_t0_0_09251.json',
    'asses_orca_mini_13b_agent_big_five_50_complete2_def_e0_t0_0_09081.json'
]

for filename in assessment_files:
    filepath = os.path.join(assessment_dir, filename)
    if os.path.exists(filepath):
        print(f'\nProcessing: {filename}')
        
        # Extract the questions and responses
        segments_data = extract_questions_and_responses_from_assessment(filepath)
        
        # Score each segment
        scores = []
        trait_mapping = {}
        reverse_scoring_map = {}
        
        for i, segment in enumerate(segments_data):
            criteria = f'Evaluate this response based on the Big Five dimension: {segment["dimension"]}. Score from 1-5 based on the evaluation rubric scale.'
            try:
                score = score_segment(segment, criteria, model='gemma:2b')
                scores.append(score)
                trait_mapping[len(scores)-1] = segment['trait']
                
                if segment['is_reversed']:
                    reverse_scoring_map[len(scores)-1] = True
            except:
                scores.append(3.0)  # Default neutral score
                trait_mapping[len(scores)-1] = segment['trait']
        
        # Calculate Big Five scores
        big_five_scores = calculate_big_five(
            scores, 
            trait_mapping, 
            reverse_scoring_map, 
            scale_range=(1, 5)
        )
        
        print(f'Big Five Results: {big_five_scores}')
        print(f'Average Score: {sum(scores)/len(scores):.2f}')
    else:
        print(f'File not found: {filename}')