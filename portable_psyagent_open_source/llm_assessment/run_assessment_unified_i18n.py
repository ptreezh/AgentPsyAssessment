import sys
import os
import json
import argparse
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

# Import internationalization support
from i18n import i18n

def main():
    """
    Main function for the PSY2 assessment with internationalization support.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='PSY2 Assessment Tool')
    parser.add_argument('--language', choices=['en', 'zh'], default='en', 
                        help='Language for the assessment (default: en)')
    parser.add_argument('--test', default='big5', 
                        help='Test to run (default: big5)')
    parser.add_argument('--role', default='a1', 
                        help='Role to use (default: a1)')
    
    args = parser.parse_args()
    
    # Set language
    i18n.set_language(args.language)
    
    # Print start message in selected language
    print(i18n.t('Starting PSY2 assessment'))
    print(f"{i18n.t('Loading test configuration')}...")
    
    # Here you would load the appropriate test and role files based on language
    # For demonstration purposes, we'll just print some translated terms
    print(f"{i18n.t('Test Results')}:")
    print(f"  {i18n.t('dimension')}: {i18n.t('Extraversion')}")
    print(f"  {i18n.t('score')}: 3.5/5.0")
    print(f"  {i18n.t('dimension')}: {i18n.t('Agreeableness')}")
    print(f"  {i18n.t('score')}: 4.2/5.0")
    
    print(f"\n{i18n.t('Analysis complete')}!")

if __name__ == '__main__':
    main()