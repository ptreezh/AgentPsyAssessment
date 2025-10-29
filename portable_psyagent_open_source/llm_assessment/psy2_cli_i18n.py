import sys
import os
import argparse

# Add the project root to the Python path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from i18n import i18n

def run_psy2_cli():
    """
    Run the PSY2 CLI with internationalization support.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='PSY2 Assessment Tool CLI')
    parser.add_argument('--language', choices=['en', 'zh'], default='en', 
                        help='Language for the assessment (default: en)')
    parser.add_argument('--interactive', action='store_true',
                        help='Run in interactive mode')
    
    args = parser.parse_args()
    
    # Set language
    i18n.set_language(args.language)
    
    # Print welcome message
    print("=" * 50)
    print(f"PSY2 - {i18n.t('Starting PSY2 assessment')}")
    print("=" * 50)
    
    if args.interactive:
        run_interactive_mode()
    else:
        run_batch_mode()

def run_interactive_mode():
    """
    Run the CLI in interactive mode.
    """
    print(f"\n{i18n.t('Starting PSY2 assessment')}...")
    print(f"{i18n.t('Loading test configuration')}...")
    
    # Simulate test execution
    print(f"\n{i18n.t('Running scenario')} 1/3...")
    print(f"{i18n.t('scenario')}: Team building activity")
    print(f"{i18n.t('prompt')}: How would you liven up the atmosphere?")
    
    # Get user input
    response = input(f"\n{i18n.t('Please enter your response')}: ")
    
    # Simulate analysis
    print(f"\n{i18n.t('Analysis complete')}!")
    print(f"\n{i18n.t('Test Results')}:")
    print(f"  {i18n.t('dimension')}: {i18n.t('Extraversion')} - {i18n.t('score')}: 4.0/5.0")
    print(f"  {i18n.t('dimension')}: {i18n.t('Agreeableness')} - {i18n.t('score')}: 3.5/5.0")

def run_batch_mode():
    """
    Run the CLI in batch mode.
    """
    print(f"\n{i18n.t('Starting PSY2 assessment')}...")
    print(f"{i18n.t('Loading test configuration')}...")
    
    # Simulate batch execution
    scenarios = [
        {"id": 1, "name": "Team Building"},
        {"id": 2, "name": "Helping Colleague"},
        {"id": 3, "name": "Project Perfection"}
    ]
    
    for scenario in scenarios:
        print(f"\n{i18n.t('Running scenario')} {scenario['id']}/3: {scenario['name']}...")
    
    print(f"\n{i18n.t('Analysis complete')}!")
    print(f"\n{i18n.t('Test Results')}:")
    print(f"  {i18n.t('Overall Score')}: 3.8/5.0")
    print(f"  {i18n.t('Detailed Analysis')}: See results/report.json")

if __name__ == '__main__':
    run_psy2_cli()