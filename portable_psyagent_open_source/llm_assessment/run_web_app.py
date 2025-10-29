#!/usr/bin/env python3
"""
Run the Psy2 Human Assessment Web App
"""

import os
import sys
import subprocess

def main():
    """Main function to run the web app"""
    print("Starting Psy2 Human Assessment Web App...")
    
    # Change to the web_app directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    web_app_dir = os.path.join(project_root, 'human_assessment', 'web_app')
    
    if not os.path.exists(web_app_dir):
        print(f"Error: Web app directory not found at {web_app_dir}")
        sys.exit(1)
        
    # Run the application using uvicorn
    try:
        print("Starting the application server...")
        print("The app will be available at http://127.0.0.1:8000")
        print("Press CTRL+C to stop the server")
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "127.0.0.1", 
            "--port", "8000"
        ], check=True, cwd=web_app_dir)
    except subprocess.CalledProcessError as e:
        print(f"Error starting the application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()