import re
from pathlib import Path
from typing import Dict, Any
import json

def extract_parameters_from_filename(filename: str) -> Dict[str, Any]:
    """
    Extract model, role, emotional stress, temperature, cognitive trap, and date from the filename.
    
    Expected filename format:
    asses_{model}_agent_big_five_50_complete2_{role}_e{emotional_stress}_t{temperature}_{cognitive_trap}_{date}{sequence}.json
    
    Examples:
    - asses_deepseek_r1_70b_agent_big_five_50_complete2_b5_e0_t0_0_09271.json
    """
    # Extract the base name without extension
    basename = Path(filename).stem
    
    # Pattern breakdown:
    # asses_{model}_agent_big_five_50_complete2_{role}_e{num}_t{num}_{cognitive_trap}_{date}{sequence}
    # Example: asses_deepseek_r1_70b_agent_big_five_50_complete2_b5_e0_t0_0_09271
    pattern = r'asses_([a-zA-Z0-9_]+)_agent_big_five_50_complete2_([a-zA-Z0-9]+)_e(\d+)_t(\d+)_([a-zA-Z0-9]+)_(\d{4})\d+'
    
    match = re.match(pattern, basename)
    
    if not match:
        raise ValueError(f"Could not parse filename: {filename}")
    
    model = match.group(1).replace('_', ' ')
    role = match.group(2)
    emotional_stress = int(match.group(3))
    temperature = int(match.group(4))
    cognitive_trap = match.group(5)
    date = match.group(6)
    
    return {
        'model': model,
        'role': role,
        'emotional_stress': emotional_stress,
        'temperature': temperature,
        'cognitive_trap': cognitive_trap,
        'date': date
    }


def create_parameter_analysis_table(filenames):
    """
    Create a parameter analysis table from a list of assessment report filenames.
    
    Args:
        filenames: List of filenames to analyze
        
    Returns:
        List of dictionaries containing extracted parameters for each file
    """
    analysis_data = []
    
    for filename in filenames:
        try:
            params = extract_parameters_from_filename(filename)
            params['filename'] = filename
            analysis_data.append(params)
        except ValueError as e:
            print(f"Error processing {filename}: {e}")
            continue  # Skip files that can't be parsed
            
    return analysis_data


def format_analysis_table(analysis_data):
    """
    Format the analysis data as a markdown table string.
    
    Args:
        analysis_data: List of dictionaries with parameter data
        
    Returns:
        Formatted markdown table as string
    """
    if not analysis_data:
        return "No valid files to analyze."
    
    # Create markdown table header
    table = "| Model | Role | Emotional Stress | Temperature | Cognitive Trap | Date | Filename |\n"
    table += "|-------|------|------------------|-------------|----------------|------|----------|\n"
    
    # Add rows
    for data in analysis_data:
        table += f"| {data['model']} | {data['role']} | {data['emotional_stress']} | {data['temperature']} | {data['cognitive_trap']} | {data['date']} | {data['filename']} |\n"
    
    return table


def process_assessment_reports(report_directory):
    """
    Process all assessment reports in a directory and create a parameter analysis table.
    
    Args:
        report_directory: Path to directory containing assessment report JSON files
        
    Returns:
        Formatted markdown table with parameter analysis
    """
    directory_path = Path(report_directory)
    
    # Find all JSON files in the directory
    json_files = list(directory_path.glob("*.json"))
    
    # Extract just the filenames
    filenames = [f.name for f in json_files]
    
    # Perform analysis
    analysis_data = create_parameter_analysis_table(filenames)
    
    # Format as table
    table = format_analysis_table(analysis_data)
    
    return table


if __name__ == "__main__":
    # Example usage
    # For testing with sample filenames
    sample_filenames = [
        "asses_deepseek_r1_70b_agent_big_five_50_complete2_b5_e0_t0_0_09271.json",
        "asses_gemma3_latest_agent_big_five_50_complete2_def_e0_t0_4k_09201.json",
        "asses_deepseek_r1_8b_agent_big_five_50_complete2_def_e0_t0_0_09091.json",
        "asses_glm4_9b_agent_big_five_50_complete2_a10_e0_t0_0_09131.json"
    ]
    
    analysis_data = create_parameter_analysis_table(sample_filenames)
    table = format_analysis_table(analysis_data)
    print(table)