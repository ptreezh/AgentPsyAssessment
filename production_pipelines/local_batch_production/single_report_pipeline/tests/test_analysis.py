import unittest
from src.analysis import detect_discrepancy, aggregate_scores, calculate_big_five, generate_report


class TestAnalysis(unittest.TestCase):
    
    def test_detect_discrepancy_returns_true_for_clear_discrepancy(self):
        """Task 3.1: Test that discrepancy detection returns True for clear discrepancy"""
        scores = [1, 5, 2, 1, 2]  # Clear discrepancy between 5 and the others
        result = detect_discrepancy(scores)
        self.assertTrue(result)
    
    def test_detect_discrepancy_returns_false_for_no_discrepancy(self):
        """Task 3.3: Test that discrepancy detection returns False for scores with no discrepancy"""
        scores = [3, 4, 3, 4, 3]  # Scores are close to each other
        result = detect_discrepancy(scores)
        self.assertFalse(result)
    
    def test_aggregate_scores_returns_correct_value(self):
        """Task 3.5: Test that final score aggregation function returns correct value"""
        scores = [1, 5, 4, 2, 3]  # Should return median which is 3
        result = aggregate_scores(scores)
        self.assertEqual(result, 3)  # Using median as aggregation method)
    
    def test_calculate_big_five_scores(self):
        """Task 4.1: Test that Big Five calculation returns correct trait scores"""
        # Example scores for 10 different personality questions
        # Each question corresponds to a trait (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism)
        # Using a simpler example: 10 questions, 2 per trait
        all_scores = [5, 3, 4, 2, 1, 6, 3, 4, 2, 5]  # 10 scores total
        
        # Define mapping from question index to Big Five trait
        # Questions 0, 5 -> Openness (O)
        # Questions 1, 6 -> Conscientiousness (C)
        # Questions 2, 7 -> Extraversion (E)
        # Questions 3, 8 -> Agreeableness (A)
        # Questions 4, 9 -> Neuroticism (N)
        trait_mapping = {
            0: 'O', 1: 'C', 2: 'E', 3: 'A', 4: 'N',
            5: 'O', 6: 'C', 7: 'E', 8: 'A', 9: 'N'
        }
        
        # For this example, let's say question 4 (Neuroticism) is reverse scored
        result = calculate_big_five(all_scores, trait_mapping, reverse_scoring_map={4: True, 9: True})
        
        # With the scores and mappings (using default 1-5 scale):
        # O: questions 0, 5 -> scores [5, 6] -> this is wrong, we're using 1-5 scale
        # Let me fix the example to use a 1-5 scale properly
        all_scores = [5, 3, 4, 2, 1, 5, 3, 4, 2, 3]  # Using 1-5 scale
        
        # Define mapping from question index to Big Five trait
        trait_mapping = {
            0: 'O', 1: 'C', 2: 'E', 3: 'A', 4: 'N',
            5: 'O', 6: 'C', 7: 'E', 8: 'A', 9: 'N'
        }
        
        # For this example, let's say question 4 (Neuroticism) and question 9 are reverse scored
        result = calculate_big_five(all_scores, trait_mapping, reverse_scoring_map={4: True, 9: True}, scale_range=(1, 5))
        
        # With the scores and mappings using 1-5 scale with reverse scoring (reverse = 6 - original):
        # O: questions 0, 5 -> scores [5, 5] -> average = 5.0
        # C: questions 1, 6 -> scores [3, 3] -> average = 3.0
        # E: questions 2, 7 -> scores [4, 4] -> average = 4.0
        # A: questions 3, 8 -> scores [2, 2] -> average = 2.0
        # N: questions 4, 9 -> scores [1, 3], reversed -> [5, 3] -> average = 4.0
        expected_traits = {'O': 5.0, 'C': 3.0, 'E': 4.0, 'A': 2.0, 'N': 4.0}  # N = (5+3)/2 = 4.0
        
        self.assertEqual(result, expected_traits)
    
    def test_generate_final_report_format(self):
        """Task 4.3: Test that final report generation produces correctly formatted output"""
        metadata = {
            'report_id': 'R001',
            'subject_id': 'S001',
            'date': '2023-01-01'
        }
        
        analysis_results = {
            'big_five': {'O': 4.2, 'C': 3.8, 'E': 2.1, 'A': 4.5, 'N': 1.9},
            'aggregate_score': 3.5,
            'discrepancy_detected': False
        }
        
        result = generate_report(metadata, analysis_results)
        
        # Check that the report contains key elements
        self.assertIn('Personality Assessment Report', result)
        self.assertIn('Report ID: R001', result)
        self.assertIn('Subject ID: S001', result)
        self.assertIn('Date: 2023-01-01', result)
        self.assertIn('Big Five Scores:', result)
        self.assertIn('Openness: 4.2', result)
        self.assertIn('Conscientiousness: 3.8', result)
        self.assertIn('Extraversion: 2.1', result)
        self.assertIn('Agreeableness: 4.5', result)
        self.assertIn('Neuroticism: 1.9', result)
        self.assertIn('Aggregate Score: 3.5', result)