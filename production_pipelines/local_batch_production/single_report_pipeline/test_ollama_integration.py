"""
Test script to verify Ollama integration
"""
import ollama
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scoring import score_segment

def test_ollama_connection():
    """Test if Ollama is accessible"""
    try:
        # Test with a simple model call
        response = ollama.generate(model='gemma:2b', prompt='Hello, how are you?')
        print("Ollama connection successful!")
        print(f"Response: {response['response'][:100]}...")  # Print first 100 chars
        return True
    except Exception as e:
        print(f"Ollama connection failed: {e}")
        print("Make sure Ollama is installed and running with at least one model pulled (e.g., 'ollama pull llama2')")
        return False

def test_real_scoring():
    """Test real scoring with Ollama"""
    test_segment = {
        'question': 'Question: How do you handle stress?',
        'answer': 'Answer: I usually take a walk or meditate to calm down.',
        'criteria': 'Effectiveness of stress management techniques'
    }
    
    try:
        score = score_segment(test_segment, 'Evaluate stress management on a scale of 1-10', model='gemma:2b')
        print(f"Real scoring result: {score}")
        return True
    except Exception as e:
        print(f"Real scoring failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Ollama integration...")
    
    if test_ollama_connection():
        print("\nTesting real scoring...")
        test_real_scoring()
    else:
        print("\nSkipping real scoring test due to connection failure.")