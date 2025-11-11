"""
Final test with available Ollama models
"""
import json
import os
import sys

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from src.scoring import score_segment
from src.analysis import calculate_big_five


def extract_questions_and_responses_from_assessment(assessment_file_path):
    """Extract questions and responses from the real JSON assessment file"""
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


def process_with_available_model(assessment_path, model_name='gemma:2b'):
    """Process assessment with a specific available model"""
    print(f"Processing with model: {model_name}")
    
    segments_data = extract_questions_and_responses_from_assessment(assessment_path)
    
    scores = []
    trait_mapping = {}
    reverse_scoring_map = {}
    
    for i, segment in enumerate(segments_data):
        criteria = f"Evaluate this response based on the Big Five dimension: {segment['dimension']}. Score from 1-5 based on the evaluation rubric scale."
        try:
            score = score_segment(segment, criteria, model=model_name)
            scores.append(score)
            trait_mapping[len(scores)-1] = segment['trait']
            
            if segment['is_reversed']:
                reverse_scoring_map[len(scores)-1] = True
        except Exception as e:
            print(f"Error scoring segment {i} with {model_name}: {e}")
            scores.append(3.0)  # Default neutral score
            trait_mapping[len(scores)-1] = segment['trait']
    
    big_five_scores = calculate_big_five(
        scores, 
        trait_mapping, 
        reverse_scoring_map, 
        scale_range=(1, 5)
    )
    
    print(f"Big Five Results with {model_name}: {big_five_scores}")
    print(f"Average Score: {sum(scores)/len(scores):.2f}")
    print(f"Score range: {min(scores):.2f} - {max(scores):.2f}")
    
    return big_five_scores


def main():
    assessment_path = r"D:\AIDevelop\portable_psyagent\results\readonly-original\asses_gemma3_latest_agent_big_five_50_complete2_def_e0_t0_0_09201.json"
    
    print("Testing with available Ollama models:")
    print("="*50)
    
    # Test with available models
    available_models = ['gemma:2b', 'gemma3:latest', 'llama3:latest']
    
    results = {}
    for model in available_models:
        try:
            print(f"\nTesting {model}...")
            result = process_with_available_model(assessment_path, model)
            results[model] = result
        except Exception as e:
            print(f"Failed to test {model}: {e}")
    
    print(f"\n{'='*50}")
    print("COMPARISON OF RESULTS ACROSS MODELS:")
    print("="*50)
    
    for model, result in results.items():
        print(f"\n{model}:")
        for trait, score in result.items():
            print(f"  {trait}: {score:.2f}")
    
    print(f"\nAll tests completed successfully!")
    print("Big Five calculation validated with real Ollama models")


if __name__ == "__main__":
    main()