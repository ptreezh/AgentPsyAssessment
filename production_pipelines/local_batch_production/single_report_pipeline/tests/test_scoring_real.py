import unittest
import time
from src.scoring import parse_score_from_response, score_segment


class TestScoringRealIntegration(unittest.TestCase):
    
    def test_parse_score_from_response_various_formats(self):
        """Task 2.1: Test parsing scores from various LLM text responses (already tested in unit tests)"""
        test_cases = [
            ("Score: 4", 4),
            ("The score is 3", 3),
            ("This is a 5.", 5),
            ("Rating: 7 out of 10", 7),
            ("Final score: 2.5", 2.5),
            ("Assessment: 8/10", 8),
            ("Score: 4\nAdditional text", 4),
            ("Text before score 6 after", 6)
        ]
        
        for response, expected_score in test_cases:
            with self.subTest(response=response):
                result = parse_score_from_response(response)
                self.assertEqual(result, expected_score)
    
    def test_score_segment_with_real_ollama_call(self):
        """Test scoring with real Ollama API call"""
        # Create a test segment and criteria
        test_segment = {
            'question': 'Question 1: How do you handle stress?',
            'answer': 'Answer: I usually take a walk or meditate.',
            'criteria': 'Stress management effectiveness (1-10 scale)'
        }
        test_criteria = 'Evaluate the effectiveness of stress management techniques described on a 1-10 scale'
        
        # Try with a model that we know works from our test
        result = score_segment(test_segment, test_criteria, model='gemma:2b')
        
        # Verify that the result is a number (the score)
        self.assertIsInstance(result, (int, float))
        # Score should be between 0 and 10 based on our criteria
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 10)
    
    def test_score_segment_with_different_models(self):
        """Test scoring with different Ollama models"""
        test_segment = {
            'question': 'Question 2: What are your social habits?',
            'answer': 'Answer: I enjoy spending time with friends on weekends.',
            'criteria': 'Social interaction patterns'
        }
        test_criteria = 'Evaluate the quality of social interaction patterns on a 1-10 scale'
        
        # Test with different models if available
        # Using models that are likely to be available or small enough to run quickly
        models_to_test = ['gemma:2b', 'phi', 'llama2']
        
        successful_models = 0
        
        for model in models_to_test:
            try:
                result = score_segment(test_segment, test_criteria, model=model)
                
                # Verify that the result is a number
                self.assertIsInstance(result, (int, float))
                self.assertGreaterEqual(result, 0)
                self.assertLessEqual(result, 10)
                
                successful_models += 1
                
                # Add a small delay to avoid overwhelming the API
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Model {model} not available, skipping: {e}")
                # Continue to the next model instead of failing the test
                continue
        
        # At least one model should work
        self.assertGreaterEqual(successful_models, 1, f"No models were available for testing. Successful models: {successful_models}")