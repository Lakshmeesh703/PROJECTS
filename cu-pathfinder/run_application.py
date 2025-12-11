#!/usr/bin/env python3
"""
Chanakya University PathFinder - Unified Application Launcher
===========================================================

This script starts both the backend Flask server and opens the frontend
in the default web browser, providing a seamless single-command startup.

Usage:
    python run_application.py [options]

Options:
    --port PORT     : Port for backend server (default: 5000)
    --debug        : Run in debug mode
    --no-browser   : Don't open browser automatically
    --backend-only : Run only backend server
    --help         : Show this help message

Author: Chanakya University PathFinder Team
Date: September 2025
"""

import os
import sys
import argparse
import subprocess
import time
import webbrowser
import threading
from pathlib import Path

# Add backend directory to Python path
project_root = Path(__file__).parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

def check_requirements():
    """Check if required packages are installed."""
    required_packages = [
        'flask',
        'flask_cors',
        'matplotlib',
        'numpy',
        'networkx'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   • {package}")
        print("\n💡 Install with: pip install -r requirements.txt")
        return False
    
    return True

def start_backend_server(port=5000, debug=False):
    """Start the Flask backend server."""
    print(f"🚀 Starting Chanakya University PathFinder Backend Server on port {port}...")
    
    # Change to backend directory
    os.chdir(backend_path)
    
    # Set environment variables
    env = os.environ.copy()
    env['PORT'] = str(port)
    env['DEBUG'] = str(debug).lower()
    env['PYTHONPATH'] = str(backend_path)
    
    try:
        # Start Flask server
        cmd = [sys.executable, "app.py"]
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        return process
        
    except Exception as e:
        print(f"❌ Error starting backend server: {e}")
        return None

def wait_for_server(port=5000, timeout=30):
    """Wait for the server to be ready."""
    import urllib.request
    import urllib.error
    
    url = f"http://localhost:{port}/api/health"
    start_time = time.time()
    
    print("⏳ Waiting for server to be ready...")
    
    while time.time() - start_time < timeout:
        try:
            response = urllib.request.urlopen(url, timeout=1)
            if response.getcode() == 200:
                print("✅ Backend server is ready!")
                return True
        except (urllib.error.URLError, urllib.error.HTTPError):
            pass
        time.sleep(1)
    
    print("⚠️  Server startup timeout")
    return False

def open_application(port=5000):
    """Open the application in the default web browser."""
    url = f"http://localhost:{port}"
    print(f"🌐 Opening Chanakya University PathFinder at {url}")
    
    try:
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"❌ Error opening browser: {e}")
        print(f"💡 Please manually open: {url}")
        return False

def print_application_info(port=5000):
    """Print application information and URLs."""
    print("\n" + "="*60)
    print("🎯 Chanakya University PathFinder - AI Campus Navigation System")
    print("="*60)
    print(f"🌐 Frontend URL: http://localhost:{port}")
    print(f"🔧 Backend API:  http://localhost:{port}/api")
    print(f"💚 Health Check: http://localhost:{port}/api/health")
    print("\n📋 Available Features:")
    print("   • Interactive Campus Map with real coordinates")
    print("   • AI-powered Pathfinding (BFS, DFS, UCS, A*)")
    print("   • Chatbot Navigation Assistant")
    print("   • Algorithm Performance Comparison")
    print("   • Step-by-step Route Guidance")
    print("   • Mobile-responsive Design")
    
    print("\n🔧 API Endpoints:")
    print("   • GET  /api/buildings     - List all campus buildings")
    print("   • POST /api/pathfind      - Find optimal paths")
    print("   • POST /api/compare       - Compare algorithms")
    print("   • GET  /api/building/<name> - Building details")
    
    print("\n⌨️  Controls:")
    print("   • Ctrl+C - Stop the application")
    print("="*60)

def run_application(port=5000, debug=False, no_browser=False, backend_only=False):
    """Run the complete CU PathFinder application."""
    print("🗺️  Chanakya University PathFinder - Unified Application Launcher")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        return False
    
    # Start backend server
    server_process = start_backend_server(port, debug)
    if not server_process:
        return False
    
    try:
        # Wait for server to be ready
        if not wait_for_server(port):
            print("❌ Failed to start backend server")
            server_process.terminate()
            return False
        
        # Print application information
        print_application_info(port)
        
        # Open browser if requested
        if not no_browser and not backend_only:
            # Give server a moment to fully initialize
            time.sleep(2)
            open_application(port)
        
        if backend_only:
            print(f"\n🖥️  Backend-only mode. Access API at http://localhost:{port}/api")
        else:
            print(f"\n🎉 CU PathFinder is now running!")
            print(f"   Open http://localhost:{port} in your browser")
        
        print("\n⏹️  Press Ctrl+C to stop the application")
        
        # Keep the application running
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print("\n\n⏹️  Shutting down CU PathFinder...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            print("✅ Application stopped successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error running application: {e}")
        if server_process:
            server_process.terminate()
        return False

def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="CU PathFinder - AI-Powered Campus Navigation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_application.py                    # Start with default settings
  python run_application.py --port 8080       # Use custom port
  python run_application.py --debug           # Enable debug mode
  python run_application.py --no-browser      # Don't open browser
  python run_application.py --backend-only    # API server only
        """
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=5000,
        help='Port for backend server (default: 5000)'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Run in debug mode with auto-reload'
    )
    
    parser.add_argument(
        '--no-browser', '-n',
        action='store_true',
        help="Don't open web browser automatically"
    )
    
    parser.add_argument(
        '--backend-only', '-b',
        action='store_true',
        help='Run only the backend API server'
    )
    
    args = parser.parse_args()
    
    # Run the application
    success = run_application(
        port=args.port,
        debug=args.debug,
        no_browser=args.no_browser,
        backend_only=args.backend_only
    )
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()