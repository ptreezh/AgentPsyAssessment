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
from pathlib import Path
import json

# Add the project root to the path so we can import modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description='Portable PsyAgent - Psychological Assessment Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  psyagent analyze --input data.json
  psyagent analyze --input data.json --model ollama_mistral
  psyagent batch --input-dir assessments/ --output-dir results/
  psyagent big5 --input data.json --output results.json
  psyagent config --show
        """
    )
    
    # Global options
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose output')
    parser.add_argument('--config', help='Configuration file path')
    
    # Define subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze psychological assessment data')
    analyze_parser.add_argument('--input', '-i', required=True, 
                               help='Input JSON file containing assessment data')
    analyze_parser.add_argument('--output', '-o', help='Output file for results (default: stdout)')
    analyze_parser.add_argument('--model', '-m', default='ollama_mistral',
                               help='Model to use for analysis (default: ollama_mistral)')
    analyze_parser.add_argument('--max-questions-per-segment', type=int, default=2,
                               help='Maximum number of questions per segment for analysis (default: 2)')
    
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
    
    # Motivation command
    motivation_parser = subparsers.add_parser('motivation', help='Run motivation analysis')
    motivation_parser.add_argument('--input', '-i', required=True,
                                 help='Input JSON file containing assessment data')
    motivation_parser.add_argument('--output', '-o', help='Output file for results (default: stdout)')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_parser.add_argument('--show', action='store_true', 
                              help='Show current configuration')
    config_parser.add_argument('--list-models', action='store_true',
                              help='List available models')
    
    # Version command
    subparsers.add_parser('version', help='Show version information')
    
    return parser

def run_analysis(args):
    """Run psychological assessment analysis."""
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file does not exist: {input_path}")
        return 1
    
    try:
        # Import the segmented analysis functionality
        from segmented_analysis import SegmentedPersonalityAnalyzer, test_segmented_analysis
        
        # Check if we need to run in test mode or use the full analysis
        if hasattr(args, 'max_questions_per_segment'):
            # Use the analyzer directly
            analyzer = SegmentedPersonalityAnalyzer(
                max_questions_per_segment=args.max_questions_per_segment,
                evaluator_name=args.model
            )
            
            # Load the input file
            with open(input_path, 'r', encoding='utf-8') as f:
                assessment_data = json.load(f)
            
            # Extract questions
            questions = analyzer.extract_questions(assessment_data)
            print(f"Extracted {len(questions)} questions for analysis")
            
            # Create segments
            segments = analyzer.create_segments(questions)
            print(f"Created {len(segments)} segments for analysis")
            
            # Analyze each segment and accumulate results
            for i, segment in enumerate(segments):
                print(f"Analyzing segment {i+1}/{len(segments)} with {len(segment)} questions")
                segment_analysis = analyzer.analyze_segment(segment, i+1)
                analyzer.accumulate_scores(segment_analysis['llm_response'])
            
            # Calculate final scores
            final_scores = analyzer.calculate_final_scores()
            
            # Output results
            if args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(final_scores, f, ensure_ascii=False, indent=2)
                print(f"Results saved to: {output_path}")
            else:
                print(json.dumps(final_scores, ensure_ascii=False, indent=2))
    
    except ImportError as e:
        print(f"Error importing analysis module: {e}")
        return 1
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

def run_batch_analysis(args):
    """Run batch analysis on multiple files."""
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
        
        try:
            # Create a temporary analyzer for each file
            from segmented_analysis import SegmentedPersonalityAnalyzer
            
            analyzer = SegmentedPersonalityAnalyzer(evaluator_name=args.model)
            
            # Load the input file
            with open(file_path, 'r', encoding='utf-8') as f:
                assessment_data = json.load(f)
            
            # Extract questions
            questions = analyzer.extract_questions(assessment_data)
            if not questions:
                print(f"  ! No questions found in {file_path.name}, skipping")
                continue
            
            print(f"  Found {len(questions)} questions")
            
            # Create segments
            segments = analyzer.create_segments(questions)
            print(f"  Created {len(segments)} segments")
            
            # Analyze each segment and accumulate results
            for j, segment in enumerate(segments):
                print(f"    Analyzing segment {j+1}/{len(segments)} with {len(segment)} questions")
                segment_analysis = analyzer.analyze_segment(segment, j+1)
                analyzer.accumulate_scores(segment_analysis['llm_response'])
            
            # Calculate final scores
            final_scores = analyzer.calculate_final_scores()
            
            # Save results
            output_file = output_dir / f"{file_path.stem}_analysis.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(final_scores, f, ensure_ascii=False, indent=2)
            
            print(f"  ✓ Saved results to: {output_file.name}")
            
        except Exception as e:
            print(f"  ✗ Error processing {file_path.name}: {e}")
            import traceback
            traceback.print_exc()
    
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
        
        # For now, we'll use the segmented analysis approach since that's what we know works
        from segmented_analysis import SegmentedPersonalityAnalyzer
        
        analyzer = SegmentedPersonalityAnalyzer(evaluator_name=args.model)
        
        # Load the input file
        with open(input_path, 'r', encoding='utf-8') as f:
            assessment_data = json.load(f)
        
        # Extract questions
        questions = analyzer.extract_questions(assessment_data)
        print(f"Extracted {len(questions)} questions for Big Five analysis")
        
        # Create segments
        segments = analyzer.create_segments(questions)
        print(f"Created {len(segments)} segments for analysis")
        
        # Analyze each segment and accumulate results
        for i, segment in enumerate(segments):
            print(f"Analyzing segment {i+1}/{len(segments)} with {len(segment)} questions")
            segment_analysis = analyzer.analyze_segment(segment, i+1)
            analyzer.accumulate_scores(segment_analysis['llm_response'])
        
        # Calculate final scores
        final_scores = analyzer.calculate_final_scores()
        
        # Output results
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(final_scores, f, ensure_ascii=False, indent=2)
            print(f"Big Five results saved to: {output_path}")
        else:
            print("=== Big Five Personality Analysis ===")
            print(json.dumps(final_scores, ensure_ascii=False, indent=2))
    
    except ImportError as e:
        print(f"Error importing Big Five analysis module: {e}")
        return 1
    except Exception as e:
        print(f"Error during Big Five analysis: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

def run_motivation_analysis(args):
    """Run motivation analysis."""
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file does not exist: {input_path}")
        return 1
    
    try:
        from shared_analysis.analyze_motivation import main as motivation_main
        
        # For now, adapt the segmented analysis approach for motivation
        from segmented_analysis import SegmentedPersonalityAnalyzer
        
        analyzer = SegmentedPersonalityAnalyzer(evaluator_name=args.model)
        
        # Load the input file
        with open(input_path, 'r', encoding='utf-8') as f:
            assessment_data = json.load(f)
        
        # Extract questions
        questions = analyzer.extract_questions(assessment_data)
        print(f"Extracted {len(questions)} questions for motivation analysis")
        
        # For motivation analysis, we might need a different approach
        # For now, we'll adapt the existing analyzer
        
        # Create segments
        segments = analyzer.create_segments(questions)
        print(f"Created {len(segments)} segments for analysis")
        
        # Analyze each segment and accumulate results
        for i, segment in enumerate(segments):
            print(f"Analyzing segment {i+1}/{len(segments)} with {len(segment)} questions")
            segment_analysis = analyzer.analyze_segment(segment, i+1)
            analyzer.accumulate_scores(segment_analysis['llm_response'])
        
        # Calculate final scores
        final_scores = analyzer.calculate_final_scores()
        
        # Output results
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(final_scores, f, ensure_ascii=False, indent=2)
            print(f"Motivation analysis results saved to: {output_path}")
        else:
            print("=== Motivation Analysis ===")
            print(json.dumps(final_scores, ensure_ascii=False, indent=2))
    
    except ImportError as e:
        print(f"Error importing motivation analysis module: {e}")
        return 1
    except Exception as e:
        print(f"Error during motivation analysis: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

def show_config(args):
    """Show configuration information."""
    print("=== Portable PsyAgent Configuration ===")
    print(f"Project Root: {Path(__file__).parent.parent}")
    print(f"Current Working Directory: {os.getcwd()}")
    
    # Show available models if Ollama is available
    try:
        from shared_analysis.ollama_evaluator import get_ollama_evaluators
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
            print("\nAvailable Models:")
            for name, config in evaluators.items():
                print(f"  - {name}")
        except ImportError:
            print("\nOllama not available")
    
    return 0

def show_version():
    """Show version information."""
    print("Portable PsyAgent CLI v1.0.0")
    print("Psychological Assessment Tool")
    return 0

def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 0
    
    # Set up logging based on verbosity
    if args.verbose:
        print(f"Verbose mode enabled. Processing command: {args.command}")
    
    # Route to appropriate command handler
    if args.command == 'analyze':
        return run_analysis(args)
    elif args.command == 'batch':
        return run_batch_analysis(args)
    elif args.command == 'big5':
        return run_big5_analysis(args)
    elif args.command == 'motivation':
        return run_motivation_analysis(args)
    elif args.command == 'config':
        return show_config(args)
    elif args.command == 'version':
        return show_version()
    else:
        print(f"Unknown command: {args.command}")
        return 1

if __name__ == '__main__':
    sys.exit(main())