import os
import re


def segment_report(source, is_file_path=False):
    """
    Segments a report file into individual question-answer segments.
    
    Args:
        source (str): Either a file path or the report content string
        is_file_path (bool): If True, treats source as a file path even if it doesn't have an extension
        
    Returns:
        list: List of segments, each containing question, answer, and criteria
    """
    if is_file_path or (isinstance(source, str) and os.path.exists(source)):
        if not os.path.exists(source):
            raise FileNotFoundError(f"Report file does not exist: {source}")
        with open(source, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        # Assume it's the content string directly
        content = source
    
    # Define pattern to identify question-answer-criteria blocks
    # Looking for patterns like "Question X:", "Answer:", and "Criteria:"
    pattern = r'(Question\s+\d+:[\s\S]+?)(?=Question\s+\d+:|$)'
    
    # Find all question blocks
    blocks = re.split(pattern, content, flags=re.IGNORECASE)
    
    # Filter out empty blocks and process them
    segments = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
            
        # Extract question, answer, and criteria
        question_match = re.search(r'(Question\s+\d+:[^\n]+)', block, re.IGNORECASE)
        answer_match = re.search(r'(Answer:[^\n]+)', block, re.IGNORECASE)
        criteria_match = re.search(r'(Criteria:[^\n]+)', block, re.IGNORECASE)
        
        if question_match and answer_match:
            segment = {
                'question': question_match.group(1).strip(),
                'answer': answer_match.group(1).strip(),
                'criteria': criteria_match.group(1).strip() if criteria_match else ''
            }
            segments.append(segment)
    
    return segments