import re
import ollama


def parse_score_from_response(response):
    """
    Parses a numeric score from an LLM response text.
    
    Args:
        response (str): The LLM response text
        
    Returns:
        float: The parsed numeric score
    """
    # Look for patterns like "Score: X", "X out of Y", "X/Y", etc.
    patterns = [
        r'score[:\s]+(\d+\.?\d*)',          # Score: X or Score X
        r'rating[:\s]+(\d+\.?\d*)',        # Rating: X
        r'(\d+\.?\d*)\s+out\s+of',         # X out of Y
        r'(\d+\.?\d*)[\/:]\d+',            # X/Y or X:Y
        r'(\d+\.?\d*)',                    # Just a number
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, response, re.IGNORECASE)
        if matches:
            # Take the first match and convert to float
            score = matches[0]
            try:
                return float(score)
            except ValueError:
                continue
    
    # If no pattern matches, return 0 as default
    return 0.0


def score_segment(segment, criteria, model='deepseek-r1:8b'):
    """
    Scores a single segment using an LLM based on given criteria.
    
    Args:
        segment (dict): A segment containing question, answer, and other data
        criteria (str): The criteria to evaluate against
        model (str): The Ollama model to use for scoring
        
    Returns:
        float: The score assigned by the LLM
    """
    # Construct the prompt for the LLM
    prompt = f"""
    {segment['question']}
    {segment['answer']}
    
    Criteria: {criteria}
    
    Evaluate the response according to the criteria above and provide a numeric score.
    Respond with only the score in the format "Score: X".
    """
    
    try:
        # Call the Ollama API
        response = call_llm_api(prompt.strip(), model)
    except Exception as e:
        raise e  # Re-raise the exception so tests can catch it
    
    # Parse the score from the response
    score = parse_score_from_response(response)
    
    return score


def call_llm_api(prompt, model='llama2'):
    """
    Calls the Ollama API with the given prompt.
    
    Args:
        prompt (str): The prompt to send to the LLM
        model (str): The Ollama model to use
        
    Returns:
        str: The response from the LLM
    """
    response = ollama.generate(model=model, prompt=prompt)
    return response['response']