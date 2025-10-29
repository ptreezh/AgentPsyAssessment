"""
Robust Assessment Runner
A wrapper around run_assessment_unified.py to provide retry logic and robust execution.
"""

import sys
import os
import time
import json
import argparse
from datetime import datetime
from typing import Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.llm_client import LLMClient
from run_assessment_unified import (
    test_model_connectivity,
    load_test_data,
    load_role_prompt,
    run_assessment,  # Import the core function
    save_results,
    TEST_ABBREVIATIONS
)


def run_assessment_with_retries(
    client,
    model_id: str,
    test_data: Dict[str, Any],
    config: dict,
    debug: bool = False,
    max_retries: int = 3,
    retry_delay: int = 5
) -> Optional[Dict[str, Any]]:
    """
    Run an assessment with retry logic.

    Args:
        client: An instance of LLMClient.
        model_id (str): The identifier for the model to be tested.
        test_data (dict): The loaded test data.
        config (dict): Configuration dictionary containing all parameters.
        debug (bool, optional): Enable debug output. Defaults to False.
        max_retries (int, optional): Maximum number of retries on failure. Defaults to 3.
        retry_delay (int, optional): Delay in seconds between retries. Defaults to 5.

    Returns:
        dict or None: The full assessment results if successful, otherwise None.
    """
    attempt = 0
    while attempt <= max_retries:
        try:
            print(f"Attempt {attempt + 1}/{max_retries + 1} for model {model_id}", flush=True)
            full_results = run_assessment(
                client, model_id, test_data, config, debug
            )
            
            # Check if run_assessment returned None (aborted due to high error rate)
            if full_results is not None:
                print(f"Assessment completed successfully on attempt {attempt + 1}.", flush=True)
                return full_results
            else:
                print(f"Assessment failed (aborted due to high error rate) on attempt {attempt + 1}.", flush=True)
                
        except Exception as e:
            print(f"Exception occurred during assessment on attempt {attempt + 1}: {e}", flush=True)
            import traceback
            traceback.print_exc()
            
        attempt += 1
        if attempt <= max_retries:
            print(f"Retrying in {retry_delay} seconds...", flush=True)
            time.sleep(retry_delay)
            
    print(f"All {max_retries + 1} attempts failed for model {model_id}.", flush=True)
    return None


def main():
    """
    Main entry point for the robust assessment tool.
    """
    parser = argparse.ArgumentParser(description='Run robust LLM assessment with advanced stress testing')
    
    # Original arguments
    parser.add_argument('--model_name', type=str, required=True, 
                       help='Model identifier (e.g., ollama/gemma3:latest)')
    parser.add_argument('--test_file', type=str, required=True, 
                       help='Test file name or path (e.g., big5, graph, or full path)')
    parser.add_argument('--role_name', type=str, required=True, 
                       help='Role name (e.g., a1, b2)')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug mode')
    parser.add_argument('--test_connection', action='store_true', 
                       help='Test model connectivity only')
    parser.add_argument('--max_retries', type=int, default=3,
                       help='Maximum number of retries on failure')
    parser.add_argument('--retry_delay', type=int, default=5,
                       help='Delay in seconds between retries')
    
    # New stress testing arguments (ASTF-FR-01)
    parser.add_argument('-esL', '--emotional-stress-level', type=int, default=0, choices=range(0, 5),
                       help='Emotional stress level (0-4)')
    parser.add_argument('-ct', '--cognitive-trap-type', type=str, choices=['p', 'c', 's', 'r'],
                       help='Cognitive trap type: p (paradox), c (circularity), s (semantic_fallacy), r (procedural)')
    parser.add_argument('-clT', '--context-load-tokens', type=int, default=0,
                       help='Context load in tokens (e.g., 1024, 2048)')
    
    args = parser.parse_args()
    
    # Handle test file abbreviation
    if args.test_file in TEST_ABBREVIATIONS:
        test_file_path = os.path.join("test_files", TEST_ABBREVIATIONS[args.test_file])
    else:
        test_file_path = args.test_file
    
    # Test connectivity only if requested
    if args.test_connection:
        success = test_model_connectivity(args.model_name)
        sys.exit(0 if success else 1)
    
    # Load test data
    try:
        test_data = load_test_data(test_file_path)
    except Exception as e:
        print(f"Error loading test data: {e}")
        sys.exit(1)
    
    # Initialize LLM client
    client = LLMClient()
    
    # Prepare configuration
    config = {
        'role_name': args.role_name,
        'test_file': args.test_file,
        'emotional_stress_level': args.emotional_stress_level,
        'cognitive_trap_type': args.cognitive_trap_type,
        'context_load_tokens': args.context_load_tokens,
        'debug': args.debug
    }
    
    # Run assessment with retries
    print(f"Starting robust assessment with stress factors:")
    print(f"  Emotional stress level: {args.emotional_stress_level}")
    print(f"  Cognitive trap type: {args.cognitive_trap_type}")
    print(f"  Context load tokens: {args.context_load_tokens}")
    print(f"  Max retries: {args.max_retries}")
    print(f"  Retry delay: {args.retry_delay}")
    
    try:
        results = run_assessment_with_retries(
            client, args.model_name, test_data, config, args.debug, 
            args.max_retries, args.retry_delay
        )
        
        if results:
            # Save results
            save_results(results, args.model_name, args.test_file, args.role_name,
                        args.emotional_stress_level, args.cognitive_trap_type, args.context_load_tokens)
            print("Robust assessment completed successfully!")
        else:
            print("Robust assessment failed after all retries!")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error during robust assessment: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()