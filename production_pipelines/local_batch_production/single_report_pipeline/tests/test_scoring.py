import unittest
from unittest.mock import patch
from src.scoring import parse_score_from_response, score_segment


class TestScoring(unittest.TestCase):
    
    def test_parse_score_from_response_various_formats(self):
        """Task 2.1: Test parsing scores from various mock LLM text responses"""
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
    
    @patch('src.scoring.call_llm_api')
    def test_score_segment_calls_api_with_correct_prompt(self, mock_api_call):
        """Task 2.3: Test that the main scoring function calls the mock API with correct prompt"""
        # Mock response from the API
        mock_api_call.return_value = "Score: 7.5"
        
        # Create a test segment and criteria
        test_segment = {
            'question': 'Question 1: How do you handle stress?',
            'answer': 'Answer: I usually take a walk or meditate.',
            'criteria': 'Stress management effectiveness'
        }
        test_criteria = 'Evaluate the effectiveness of stress management techniques described'
        
        # Call the function with default model
        result = score_segment(test_segment, test_criteria, model='llama2')
        
        # Verify that the API was called with the expected prompt
        mock_api_call.assert_called_once()
        call_args = mock_api_call.call_args[0][0]  # First argument of the call
        
        # Check that the prompt contains necessary elements
        self.assertIn(test_segment['question'], call_args)
        self.assertIn(test_segment['answer'], call_args)
        self.assertIn(test_criteria, call_args)
        
        # Verify the result is the parsed score
        self.assertEqual(result, 7.5)