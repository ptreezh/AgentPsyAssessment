import unittest
from src.segmentation import segment_report


class TestSegmentation(unittest.TestCase):
    
    def test_segment_report_raises_exception_for_nonexistent_file(self):
        """Task 1.1: Test that an exception is raised if the source report file does not exist"""
        with self.assertRaises(FileNotFoundError):
            segment_report("nonexistent_file.txt", is_file_path=True)
    
    def test_segment_report_returns_correct_number_of_segments(self):
        """Task 1.3: Test that segmentation function returns correct number of segments"""
        mock_report = """
        Question 1: How do you handle stress?
        Answer: I usually take a walk or meditate.
        Criteria: Stress management techniques
        
        Question 2: What are your social habits?
        Answer: I enjoy spending time with friends on weekends.
        Criteria: Social behavior patterns
        
        Question 3: How do you approach problems?
        Answer: I analyze the situation and try different solutions.
        Criteria: Problem-solving approach
        """
        
        segments = segment_report(mock_report)
        self.assertEqual(len(segments), 3)
    
    def test_segment_content_correctly_formatted(self):
        """Task 1.5: Test that the content of a single generated segment is correctly formatted"""
        mock_report = """
        Question 1: How do you handle stress?
        Answer: I usually take a walk or meditate.
        Criteria: Stress management techniques
        """
        
        segments = segment_report(mock_report)
        self.assertEqual(len(segments), 1)
        
        segment = segments[0]
        self.assertIn('question', segment)
        self.assertIn('answer', segment)
        self.assertIn('criteria', segment)
        self.assertTrue(segment['question'].startswith('Question 1:'))
        self.assertTrue(segment['answer'].startswith('Answer:'))
        self.assertTrue(segment['criteria'].startswith('Criteria:'))