@echo off
REM Quick deployment script for copying files to project root (Windows)

echo 📦 Copying deployment files to project root...

REM Copy files
copy requirements.txt ..\requirements.txt
copy Procfile ..\Procfile
copy wsgi.py ..\wsgi.py
copy runtime.txt ..\runtime.txt
copy .gitignore ..\.gitignore

echo.
echo ✅ Files copied successfully!
echo.
echo 📋 Next steps:
echo 1. Update Kaggle credentials handling (see kaggle_env_update.py)
echo 2. Test locally: gunicorn wsgi:app --bind 0.0.0.0:5000
echo 3. Push to GitHub
echo 4. Deploy on Render/Railway/PythonAnywhere
echo.
echo 📖 Read DEPLOYMENT_GUIDE.md for detailed instructions
pause
