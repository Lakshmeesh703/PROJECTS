# FIFA World Cup 2026 Predictor - Deploy Folder

## 📂 Contents

This folder contains all files needed to deploy your FIFA predictor to GitHub and free hosting platforms.

### Files:

1. **requirements.txt** - Python dependencies for production
2. **Procfile** - Deployment configuration for Render/Railway/Heroku
3. **wsgi.py** - WSGI entry point for production servers
4. **runtime.txt** - Specifies Python version
5. **.gitignore** - Files to exclude from GitHub
6. **DEPLOYMENT_GUIDE.md** - Complete deployment instructions
7. **kaggle_env_update.py** - Instructions to update Kaggle credential handling
8. **copy_files.bat/sh** - Scripts to copy files to project root

---

## 🚀 Quick Start

### Step 1: Copy Files to Project Root
**Windows:**
```bash
cd deploy
copy_files.bat
```

**Linux/Mac:**
```bash
cd deploy
chmod +x copy_files.sh
./copy_files.sh
```

**Or manually:**
```bash
cp deploy/requirements.txt .
cp deploy/Procfile .
cp deploy/wsgi.py .
cp deploy/runtime.txt .
cp deploy/.gitignore .
```

---

### Step 2: Update Kaggle Credentials
See `kaggle_env_update.py` for code to support environment variables.

---

### Step 3: Test Locally
```bash
pip install -r requirements.txt
gunicorn wsgi:app --bind 0.0.0.0:5000
```

---

### Step 4: Deploy to GitHub
```bash
git init
git add .
git commit -m "Ready for deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/fifa-predictor.git
git push -u origin main
```

---

### Step 5: Deploy to Hosting Platform

Choose one:
- **Render** (Recommended): [render.com](https://render.com)
- **Railway**: [railway.app](https://railway.app)
- **PythonAnywhere**: [pythonanywhere.com](https://pythonanywhere.com)
- **Vercel**: [vercel.com](https://vercel.com)

See **DEPLOYMENT_GUIDE.md** for detailed platform-specific instructions.

---

## 🔐 Important Security Notes

⚠️ **NEVER commit kaggle.json to GitHub!**

Instead:
1. Add `kaggle.json` to `.gitignore` ✅
2. Set environment variables on hosting platform:
   - `KAGGLE_USERNAME`
   - `KAGGLE_KEY`

---

## 📞 Need Help?

Read **DEPLOYMENT_GUIDE.md** for:
- Platform-specific instructions
- Troubleshooting tips
- Environment variable setup
- Testing procedures

---

**Good luck! 🚀⚽**
