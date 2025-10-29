"""
Main CLI entry point for AgentPsyAssessment
This module provides a command-line interface for running psychological assessments and analyses.
"""

import argparse
import sys
import os
from llm_assessment.run_assessment_unified import main as run_assessment_main
from llm_assessment.run_batch_suite import main as run_batch_main
# Import analysis functions
try:
    from analysis.analyze_results import run_analysis
    ANALYSIS_AVAILABLE = True
except ImportError:
    ANALYSIS_AVAILABLE = False
    print("Warning: Analysis module not available. Please ensure all dependencies are installed.")

def main():
    parser = argparse.ArgumentParser(
        description="AgentPsyAssessment - Portable Psychological Assessment Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s assess --model gpt-4o --role def
  %(prog)s analyze --input results/asses_gpt-4o_def_*.json
  %(prog)s batch --model claude-3-5-sonnet --roles a1,a2,b1
  %(prog)s assess --model llama3.1 --ollama
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Assessment command
    assess_parser = subparsers.add_parser('assess', help='Run a single assessment')
    assess_parser.add_argument('--model', type=str, default='gpt-4o', help='Model to use for assessment')
    assess_parser.add_argument('--role', type=str, default='def', help='Personality role to apply')
    assess_parser.add_argument('--temperature', type=float, default=0.0, help='Model temperature')
    assess_parser.add_argument('--ollama', action='store_true', help='Use Ollama models')
    assess_parser.add_argument('--host', type=str, default='http://localhost:11434', help='Ollama host')
    assess_parser.add_argument('--context', type=str, default='', help='Additional context for assessment')
    
    # Analysis command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze assessment results')
    analyze_parser.add_argument('--input', type=str, required=True, help='Path to input assessment results')
    analyze_parser.add_argument('--analysis-type', type=str, choices=['bigfive', 'mbti', 'belbin', 'comprehensive'], 
                               default='comprehensive', help='Type of analysis to perform')
    analyze_parser.add_argument('--confidence-threshold', type=float, default=0.7, 
                               help='Confidence threshold for recommendations')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Run batch assessments')
    batch_parser.add_argument('--model', type=str, default='gpt-4o', help='Model to use for assessment')
    batch_parser.add_argument('--roles', type=str, default='a1,a2', help='Comma-separated list of roles')
    batch_parser.add_argument('--ollama', action='store_true', help='Use Ollama models')
    batch_parser.add_argument('--host', type=str, default='http://localhost:11434', help='Ollama host')
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    # Set environment variables based on arguments
    if args.ollama:
        os.environ['OLLAMA_HOST'] = args.host
        os.environ['PROVIDER'] = 'local'
    else:
        os.environ['PROVIDER'] = 'cloud'
    
    # Run the appropriate command
    try:
        if args.command == 'assess':
            # For assess command, we need to simulate command line arguments for the actual function
            sys.argv = [
                'run_assessment_unified.py',
                '--model', args.model,
                '--role', args.role,
                '--temperature', str(args.temperature)
            ]
            if args.context:
                sys.argv.extend(['--context', args.context])
            if args.ollama:
                sys.argv.append('--ollama')
                sys.argv.extend(['--host', args.host])
            
            run_assessment_main()
        elif args.command == 'batch':
            # For batch command, we need to simulate command line arguments for the actual function
            roles_list = args.roles.split(',')
            sys.argv = [
                'run_batch_suite.py',
                '--model', args.model,
                '--roles', ','.join(roles_list)
            ]
            if args.ollama:
                sys.argv.append('--ollama')
                sys.argv.extend(['--host', args.host])
            
            run_batch_main()
        elif args.command == 'analyze':
            # For analyze command, run analysis using appropriate method
            if not ANALYSIS_AVAILABLE:
                print("Error: Analysis module not available. Please ensure all dependencies are installed.")
                sys.exit(1)
            
            try:
                result = run_analysis(
                    input_file=args.input,
                    analysis_type=args.analysis_type,
                    confidence_threshold=args.confidence_threshold
                )
                print("Analysis completed successfully!")
                print(f"Input file: {args.input}")
                print(f"Analysis type: {args.analysis_type}")
            except Exception as e:
                print(f"Error during analysis: {e}", file=sys.stderr)
                sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()