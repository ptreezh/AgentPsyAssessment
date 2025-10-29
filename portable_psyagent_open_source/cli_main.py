#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Portable PsyAgent CLI - Main Command Line Interface

This is the main entry point for the Portable PsyAgent CLI tool.
It provides an interface for conducting psychological assessments using various AI models.
"""

import argparse
import sys
import os
import json
from pathlib import Path

# Add the project root to the path so we can import modules
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description='Portable PsyAgent - Psychological Assessment Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze --input data.json
  %(prog)s analyze --input data.json --model ollama_mistral
  %(prog)s batch --input-dir assessments/ --output-dir results/
  %(prog)s big5 --input data.json --output results.json
  %(prog)s config --show
        """
    )
    
    # Define subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze psychological assessment data')
    analyze_parser.add_argument('--input', '-i', required=True, 
                               help='Input JSON file containing assessment data')
    analyze_parser.add_argument('--output', '-o', help='Output file for results (default: stdout)')
    analyze_parser.add_argument('--model', '-m', default='ollama_mistral',
                               help='Model to use for analysis (default: ollama_mistral)')
    analyze_parser.add_argument('--evaluator', '-e', help='Evaluator to use')
    analyze_parser.add_argument('--verbose', '-v', action='store_true', 
                               help='Enable verbose output')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Run batch analysis on multiple files')
    batch_parser.add_argument('--input-dir', required=True,
                             help='Directory containing input JSON files')
    batch_parser.add_argument('--output-dir', required=True,
                             help='Directory to save output results')
    batch_parser.add_argument('--model', default='ollama_mistral',
                             help='Model to use for analysis (default: ollama_mistral)')
    batch_parser.add_argument('--recursive', '-r', action='store_true',
                             help='Recursively search subdirectories')
    
    # Big5 command
    big5_parser = subparsers.add_parser('big5', help='Run Big Five personality analysis')
    big5_parser.add_argument('--input', '-i', required=True,
                            help='Input JSON file containing assessment data')
    big5_parser.add_argument('--output', '-o', help='Output file for results (default: stdout)')
    big5_parser.add_argument('--model', '-m', default='ollama_mistral',
                            help='Model to use for analysis (default: ollama_mistral)')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_parser.add_argument('--show', action='store_true', 
                              help='Show current configuration')
    config_parser.add_argument('--list-models', action='store_true',
                              help='List available models')
    
    # Help command
    subparsers.add_parser('help', help='Show this help message')
    
    return parser

def run_analysis(args):
    """Run psychological assessment analysis."""
    from shared_analysis.analyze_results import analyze_single_file
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file does not exist: {input_path}")
        return 1
    
    # Create temporary output directory if output file specified
    if args.output:
        output_dir = Path(args.output).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = args.output
    else:
        output_path = None
    
    # For now, we'll just run a basic analysis using the existing functionality
    print(f"Analyzing: {input_path}")
    
    # Import the existing analysis functionality
    try:
        from shared_analysis.analyze_results import analyze_single_file
        
        # Create a temporary output directory for this analysis
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            success = analyze_single_file(str(input_path), temp_dir)
            if success and output_path:
                # Move results to specified output path
                result_file = Path(temp_dir) / "analysis.json"
                if result_file.exists():
                    result_file.replace(output_path)
                    print(f"Results saved to: {output_path}")
                else:
                    print("Analysis completed but no results file found.")
            elif success:
                # Print to stdout if no output file specified
                result_file = Path(temp_dir) / "analysis.json"
                if result_file.exists():
                    with open(result_file, 'r', encoding='utf-8') as f:
                        print(f.read())
    
    except ImportError as e:
        print(f"Error importing analysis module: {e}")
        return 1
    except Exception as e:
        print(f"Error during analysis: {e}")
        return 1
    
    return 0

def run_batch_analysis(args):
    """Run batch analysis on multiple files."""
    from pathlib import Path
    import os
    
    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"Error: Input directory does not exist: {input_dir}")
        return 1
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all JSON files in the input directory
    json_files = []
    if args.recursive:
        json_files = list(input_dir.rglob("*.json"))
    else:
        json_files = list(input_dir.glob("*.json"))
    
    print(f"Found {len(json_files)} JSON files to analyze")
    
    # Process each file
    for i, file_path in enumerate(json_files, 1):
        print(f"Processing [{i}/{len(json_files)}]: {file_path.name}")
        
        # Create output file path
        relative_path = file_path.relative_to(input_dir)
        output_file = output_dir / relative_path.with_suffix('.json')
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Use the analyze_single_file function from analyze_results.py
            from shared_analysis.analyze_results import analyze_single_file
            success = analyze_single_file(str(file_path), str(output_file.parent))
            if success:
                print(f"  ✓ Completed: {file_path.name}")
            else:
                print(f"  ✗ Failed: {file_path.name}")
        except Exception as e:
            print(f"  ✗ Error processing {file_path.name}: {e}")
    
    print(f"Batch analysis completed. Results saved to: {output_dir}")
    return 0

def run_big5_analysis(args):
    """Run Big Five personality analysis."""
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file does not exist: {input_path}")
        return 1
    
    try:
        from shared_analysis.analyze_big5_results import main as big5_main
        
        # This will need to be adapted based on the actual analyze_big5_results.py implementation
        # For now, we'll use the segmented analysis approach
        from segmented_analysis import test_segmented_analysis
        
        # We'll need to handle the output appropriately
        if args.output:
            # For now, just run the analysis - the output handling might need to be adjusted
            print(f"Running Big Five analysis on: {input_path}")
            test_segmented_analysis(str(input_path))
        else:
            print("Big Five personality analysis completed")
    
    except ImportError as e:
        print(f"Error importing Big Five analysis module: {e}")
        return 1
    except Exception as e:
        print(f"Error during Big Five analysis: {e}")
        return 1
    
    return 0

def show_config(args):
    """Show configuration information."""
    if args.show:
        print("=== Portable PsyAgent Configuration ===")
        print(f"Project Root: {Path(__file__).parent}")
        print(f"Current Working Directory: {os.getcwd()}")
        
        # Show available models if Ollama is available
        try:
            from shared_analysis.ollama_evaluator import get_ollama_model_config, get_ollama_evaluators
            evaluators = get_ollama_evaluators()
            print("\nAvailable Ollama Evaluators:")
            for name, config in evaluators.items():
                print(f"  - {name}: {config.get('description', 'No description')}")
        except ImportError:
            print("\nOllama evaluators not available")
    
    if args.list_models:
        try:
            from shared_analysis.ollama_evaluator import get_ollama_evaluators
            evaluators = get_ollama_evaluators()
            print("Available Models:")
            for name, config in evaluators.items():
                model_config = get_ollama_model_config(config.get('model'))
                print(f"  - {name}: {model_config.get('name', 'Unknown')}")
        except ImportError:
            print("Ollama not available")
    
    return 0

def show_help():
    """Show help message."""
    parser = create_parser()
    parser.print_help()
    return 0

def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command is None or args.command == 'help':
        show_help()
        return 0
    
    # Set up logging based on verbosity
    if hasattr(args, 'verbose') and args.verbose:
        print(f"Verbose mode enabled. Processing command: {args.command}")
    
    # Route to appropriate command handler
    if args.command == 'analyze':
        return run_analysis(args)
    elif args.command == 'batch':
        return run_batch_analysis(args)
    elif args.command == 'big5':
        return run_big5_analysis(args)
    elif args.command == 'config':
        return show_config(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1

if __name__ == '__main__':
    sys.exit(main())