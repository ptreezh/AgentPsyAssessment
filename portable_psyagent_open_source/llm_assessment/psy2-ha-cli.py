#!/usr/bin/env python3

"""
Entry point script for the Psy2 Human Assessment CLI.
This script allows users to run the CLI tool directly.
"""

import sys
import os

# Add the human_assessment directory to the path so we can import cli
human_assessment_path = os.path.join(os.path.dirname(__file__), 'human_assessment')
if human_assessment_path not in sys.path:
    sys.path.insert(0, human_assessment_path)

def main():
    """Main entry point for the CLI."""
    try:
        # Import and run the main CLI function
        from cli.main import main as cli_main
        cli_main()
    except ImportError as e:
        print(f"Error importing CLI module: {e}")
        print("Please ensure you are running this script from the project root directory.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()