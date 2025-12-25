# FIFA World Cup 2026 Predictor - Deployment Guide

## 🚀 Free Deployment Options

This project can be deployed for FREE on the following platforms:

### Option 1: Render (Recommended ⭐)
**Steps:**
1. Push your code to GitHub
2. Go to [render.com](https://render.com) and sign up
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn wsgi:app --bind 0.0.0.0:$PORT`
   - **Environment Variables:**
     - `KAGGLE_USERNAME` = your_kaggle_username
     - `KAGGLE_KEY` = your_kaggle_api_key
6. Click "Create Web Service"

**Free Tier:** ✅ 750 hours/month

---

### Option 2: Railway
**Steps:**
1. Push your code to GitHub
2. Go to [railway.app](https://railway.app) and sign up
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables:
   - `KAGGLE_USERNAME`
   - `KAGGLE_KEY`
6. Railway auto-detects Python and uses Procfile

**Free Tier:** ✅ $5 credit/month

---

### Option 3: PythonAnywhere
**Steps:**
1. Sign up at [pythonanywhere.com](https://pythonanywhere.com)
2. Upload your code or clone from GitHub
3. Create a web app (Flask)
4. Configure WSGI file to point to your app
5. Install requirements: `pip install -r requirements.txt`
6. Set environment variables in web app settings

**Free Tier:** ✅ 1 web app + 512MB storage

---

### Option 4: Vercel (Serverless)
**Steps:**
1. Install Vercel CLI: `npm i -g vercel`
2. Push code to GitHub
3. Run `vercel` in your project directory
4. Add environment variables in Vercel dashboard
5. Deploy automatically on git push

**Free Tier:** ✅ Unlimited deployments

---

## 📋 Pre-Deployment Checklist

### 1. Copy Files to Project Root
Copy these files from `deploy/` folder to your project root:
```bash
cp deploy/requirements.txt .
cp deploy/Procfile .
cp deploy/wsgi.py .
cp deploy/runtime.txt .
cp deploy/.gitignore .
```

### 2. Set Up Kaggle Credentials
**DO NOT** commit your `kaggle.json` file!

Instead, set environment variables on your hosting platform:
- `KAGGLE_USERNAME` = your username
- `KAGGLE_KEY` = your API key

### 3. Update Scraper to Use Environment Variables
The scraper needs to read credentials from environment variables instead of file.

### 4. Test Locally
```bash
pip install -r requirements.txt
gunicorn wsgi:app --bind 0.0.0.0:5000
```

### 5. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit for deployment"
git branch -M main
git remote add origin https://github.com/yourusername/fifa-predictor.git
git push -u origin main
```

---

## 🔐 Environment Variables Required

Set these on your hosting platform:

| Variable | Value | Example |
|----------|-------|---------|
| `KAGGLE_USERNAME` | Your Kaggle username | `your_username` |
| `KAGGLE_KEY` | Your Kaggle API key | `abc123xyz...` |
| `PORT` | Port number (auto-set by host) | `5000` |

---

## 📁 Project Structure for Deployment

```
Fifa_Predict/
├── TASK_1_Data_Collection/
├── TASK_2_Data_Preprocessing/
├── TASK_3_Model_Building/
├── TASK_4_Model_Evaluation/
├── TASK_5_Feature_Importance/
├── TASK_6_Deployment/
│   ├── app/
│   │   ├── app_flask.py
│   │   ├── data_loader.py
│   │   ├── enhanced_predictor.py
│   │   └── ...
│   └── templates/
│       └── index_flask.html
├── shared_data/
├── requirements.txt  ← Copy from deploy/
├── Procfile          ← Copy from deploy/
├── wsgi.py           ← Copy from deploy/
├── runtime.txt       ← Copy from deploy/
└── .gitignore        ← Copy from deploy/
```

---

## 🛠️ Troubleshooting

### Port Issues
Most platforms set `PORT` automatically. Your app reads it from environment:
```python
port = int(os.environ.get("PORT", 5000))
```

### Kaggle API Issues
If scraper fails, ensure:
1. Environment variables are set correctly
2. Kaggle credentials are valid
3. Dataset is public or you have access

### Memory Issues
Free tiers have limited RAM. To reduce memory:
- Disable auto-scraping on startup
- Use cached data files
- Reduce model complexity

---

## 🎯 Quick Deploy Commands

### For Render/Railway:
Just push to GitHub and connect repository.

### For Vercel:
```bash
vercel --prod
```

### For Heroku:
```bash
heroku create your-app-name
git push heroku main
```

---

## ✅ Success Criteria

Your app is successfully deployed when:
- ✅ URL loads without errors
- ✅ Homepage displays 48 teams
- ✅ Team details modal works
- ✅ Prediction system responds
- ✅ No 500 errors in logs

---

## 📞 Support

If you encounter issues:
1. Check platform logs
2. Verify environment variables
3. Test locally first with `gunicorn`
4. Check data file paths

---

**Good luck with deployment! 🚀⚽**
