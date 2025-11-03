"""
Verification script to demonstrate proper Big Five scoring implementation
"""
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from analysis import calculate_big_five


def demonstrate_big_five_scoring():
    """Demonstrate the proper Big Five scoring methodology"""
    print("Demonstrating proper Big Five scoring methodology...")
    
    # Example from a standard personality inventory using 5-point Likert scale (1-5)
    # Simulating 20 questions with different traits and some reverse-scored items
    scores = [4, 3, 5, 2, 1, 4, 3, 5, 2, 1, 4, 3, 5, 2, 1, 4, 3, 5, 2, 1]  # 20 questions, scores 1-5
    
    # Mapping each question to a Big Five trait
    trait_mapping = {}
    traits = ['O', 'C', 'E', 'A', 'N']  # Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism
    
    for i in range(20):
        trait_mapping[i] = traits[i % 5]
    
    print(f"Trait mapping: {trait_mapping}")
    print(f"Original scores: {scores}")
    
    # In standard personality inventories, some questions are reverse-scored
    # Let's say every third question starting from index 4 is reverse-scored
    reverse_scoring_map = {i: True for i in range(4, 20, 3)}  # indices 4, 7, 10, 13, 16, 19
    print(f"Reverse scoring for indices: {list(reverse_scoring_map.keys())}")
    
    # Calculate the Big Five scores with proper 1-5 scale
    big_five_scores = calculate_big_five(scores, trait_mapping, reverse_scoring_map, scale_range=(1, 5))
    
    print(f"Big Five scores: {big_five_scores}")
    
    # Show reverse scoring effect
    print("\nReverse scoring analysis (using 1-5 scale, reverse = 6 - original):")
    for idx in sorted(reverse_scoring_map.keys()):
        original_score = scores[idx]
        # Reverse scoring formula for 1-5 scale: (max + min) - original_score = 6 - original_score
        reversed_score = 6 - original_score
        trait = trait_mapping[idx]
        print(f"  Q{idx} ({trait}): {original_score} -> {reversed_score}")
    
    print("\nThis demonstrates proper Big Five methodology:")
    print("- Each question maps to a specific trait")
    print("- Uses standard Likert scale (e.g., 1-5) for responses") 
    print("- Some questions are reverse-scored per standard methodology") 
    print("- Scores are aggregated by trait to form personality profiles")
    print("- Follows established psychological assessment practices")


if __name__ == "__main__":
    demonstrate_big_five_scoring()