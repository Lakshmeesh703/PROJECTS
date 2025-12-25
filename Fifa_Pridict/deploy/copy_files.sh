#!/bin/bash

# Quick deployment script for copying files to project root

echo "📦 Copying deployment files to project root..."

# Copy files
cp requirements.txt ../requirements.txt
cp Procfile ../Procfile
cp wsgi.py ../wsgi.py
cp runtime.txt ../runtime.txt
cp .gitignore ../.gitignore

echo "✅ Files copied successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update Kaggle credentials handling (see kaggle_env_update.py)"
echo "2. Test locally: gunicorn wsgi:app --bind 0.0.0.0:5000"
echo "3. Push to GitHub"
echo "4. Deploy on Render/Railway/PythonAnywhere"
echo ""
echo "📖 Read DEPLOYMENT_GUIDE.md for detailed instructions"
