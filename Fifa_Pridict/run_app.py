#!/usr/bin/env python3
"""
FIFA World Cup 2026 Predictor - Launch Script
Run this file to start the Flask web application
"""

import webbrowser
import os
import sys
from pathlib import Path

def main():
    """Start the Flask application and open the browser"""
    
    # Change to the script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # Add TASK_6_Deployment/app to Python path
    app_path = script_dir / "TASK_6_Deployment" / "app"
    if not app_path.exists():
        print(" Error: 'TASK_6_Deployment/app/' not found!")
        print(f"Current directory: {os.getcwd()}")
        sys.exit(1)
    
    # Add app directory to sys.path
    sys.path.insert(0, str(app_path))
    
    # Import and run Flask app
    try:
        print("\nFIFA World Cup 2026 Predictor")
        print("Starting Flask server on http://localhost:5000")
        print("Press Ctrl+C to stop the server\n")
        
        # Open browser automatically after a short delay
        import threading
        def open_browser():
            import time
            time.sleep(1.5)
            webbrowser.open("http://localhost:5000")
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Import and run the Flask app
        from app_flask import app  # type: ignore # noqa: E402
        app.run(debug=False, port=5000, host='0.0.0.0')
        
    except KeyboardInterrupt:
        print("\nServer stopped")
        sys.exit(0)
    except ImportError as e:
        print(f"\nError: Could not import Flask app")
        print(f"Make sure Flask is installed: pip install flask")
        print(f"Details: {e}")
        sys.exit(1)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\nError: Port 5000 is already in use!")
            print(f"Try closing other servers or access http://localhost:5000")
        else:
            print(f"\nError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
