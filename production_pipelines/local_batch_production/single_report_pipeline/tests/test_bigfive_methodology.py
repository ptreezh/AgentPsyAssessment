"""
Additional test to verify Big Five scoring methodology is correct
"""
import unittest
from src.analysis import calculate_big_five


class TestBigFiveMethodology(unittest.TestCase):
    
    def test_big_five_with_reverse_scoring(self):
        """Test Big Five calculation with proper reverse scoring methodology"""
        # Simulate a mini-IPIP (International Personality Item Pool) like questionnaire
        # Each index represents a personality question
        
        # Example scores for 10 questions: [3, 4, 2, 5, 1, 6, 4, 3, 2, 7]
        # Trait mapping: O(0,5), C(1,6), E(2,7), A(3,8), N(4,9)
        scores = [3, 4, 2, 5, 1, 6, 4, 3, 2, 7]
        
        trait_mapping = {
            0: 'O',  # Openness
            1: 'C',  # Conscientiousness
            2: 'E',  # Extraversion
            3: 'A',  # Agreeableness
            4: 'N',  # Neuroticism (reverse scored)
            5: 'O',  # Openness
            6: 'C',  # Conscientiousness
            7: 'E',  # Extraversion
            8: 'A',  # Agreeableness
            9: 'N'   # Neuroticism (reverse scored)
        }
        
        # Questions 4 and 9 are reverse scored (common in standard personality inventories)
        reverse_scoring_map = {4: True, 9: True}
        
        # Using 1-7 scale, reverse scoring formula: (max + min) - original = 8 - original
        # Question 4: Score 1 becomes 8-1=7, question 9 score 7 becomes 8-7=1
        result = calculate_big_five(scores, trait_mapping, reverse_scoring_map, scale_range=(1, 7))
        
        # Expected calculations:
        # O: questions 0, 5 -> scores [3, 6] -> average = 4.5
        # C: questions 1, 6 -> scores [4, 4] -> average = 4.0
        # E: questions 2, 7 -> scores [2, 3] -> average = 2.5
        # A: questions 3, 8 -> scores [5, 2] -> average = 3.5
        # N: questions 4, 9 -> scores [1, 7] reversed -> [7, 1] -> average = 4.0
        
        expected = {
            'O': 4.5,
            'C': 4.0,
            'E': 2.5,
            'A': 3.5,
            'N': 4.0
        }
        
        self.assertEqual(result, expected)
    
    def test_big_five_with_no_reverse_scoring(self):
        """Test Big Five calculation without reverse scoring"""
        scores = [5, 3, 4, 2, 6, 5, 3, 4, 2, 6]
        
        trait_mapping = {
            0: 'O', 1: 'C', 2: 'E', 3: 'A', 4: 'N',
            5: 'O', 6: 'C', 7: 'E', 8: 'A', 9: 'N'
        }
        
        result = calculate_big_five(scores, trait_mapping, scale_range=(1, 7))
        
        # Expected calculations:
        # O: [5, 5] -> 5.0
        # C: [3, 3] -> 3.0
        # E: [4, 4] -> 4.0
        # A: [2, 2] -> 2.0
        # N: [6, 6] -> 6.0
        
        expected = {
            'O': 5.0,
            'C': 3.0,
            'E': 4.0,
            'A': 2.0,
            'N': 6.0
        }
        
        self.assertEqual(result, expected)
    
    def test_big_five_with_partial_traits(self):
        """Test Big Five calculation when not all traits are represented"""
        scores = [4, 5, 3, 6]  # Only 4 questions
        
        trait_mapping = {
            0: 'O',
            1: 'C',
            2: 'O',  # Another Openness question
            3: 'E'   # Extraversion
        }
        
        result = calculate_big_five(scores, trait_mapping, scale_range=(1, 7))
        
        # Expected calculations:
        # O: [4, 3] -> 3.5
        # C: [5] -> 5.0
        # E: [6] -> 6.0
        # A and N should not appear since no questions map to them
        
        expected = {
            'O': 3.5,
            'C': 5.0,
            'E': 6.0
        }
        
        self.assertEqual(result, expected)