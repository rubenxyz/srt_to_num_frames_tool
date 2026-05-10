#!/usr/bin/env python3
"""
SRT to Num Frames Tool - Entry Point

Convenient script to run the SRT to frame count conversion tool.
Auto-installs dependencies if missing, then executes main function.
"""

import subprocess
import sys
from pathlib import Path

def ensure_dependencies():
    """Check for required dependencies and install if missing."""
    required = {'srt': 'srt==3.5.3', 'natsort': 'natsort==8.4.0'}
    missing = []
    
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Installing missing dependencies: {', '.join(missing)}")
        
        # Try different installation methods based on environment
        install_methods = [
            # First try: standard install (works in venv)
            [sys.executable, '-m', 'pip', 'install', '--quiet'],
            # Second try: user install
            [sys.executable, '-m', 'pip', 'install', '--user', '--quiet'],
            # Third try: break system packages (for externally-managed environments)
            [sys.executable, '-m', 'pip', 'install', '--break-system-packages', '--quiet'],
        ]
        
        success = False
        for pip_cmd in install_methods:
            try:
                subprocess.check_call(pip_cmd + missing, stderr=subprocess.DEVNULL)
                print("Dependencies installed successfully")
                success = True
                break
            except subprocess.CalledProcessError:
                continue
        
        if not success:
            print("ERROR: Failed to install dependencies with all methods")
            print("\nPlease install manually:")
            print("  pip install -r requirements.txt")
            sys.exit(1)

if __name__ == "__main__":
    # Ensure dependencies are installed
    ensure_dependencies()
    
    # Add src directory to Python path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    # Import and run the main function
    from main import main
    
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        sys.exit(1)

