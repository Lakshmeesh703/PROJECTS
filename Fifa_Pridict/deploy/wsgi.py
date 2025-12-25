"""
WSGI Entry Point for Deployment
This file is used by production servers (Gunicorn, Render, Railway, etc.)
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Add TASK_6_Deployment/app to Python path
app_path = project_root / "TASK_6_Deployment" / "app"
sys.path.insert(0, str(app_path))

# Import the Flask application
from app_flask import app  # type: ignore

# For debugging
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
