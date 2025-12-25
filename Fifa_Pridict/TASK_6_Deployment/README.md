# TASK 6: Web Application Deployment (15 Marks)

##  Objective
Deploy machine learning models as an interactive web application for FIFA World Cup 2026 predictions.

##  Contents

### App (`app/`)
- **`app_flask.py`** - Main Flask application server
- **`data_loader.py`** - Data loading and preprocessing utilities
- **`enhanced_predictor.py`** - Enhanced prediction engine (5-factor model)
- **`fifa_26_integration.py`** - FIFA 26 player data integration

### Templates (`templates/`)
- **`index_flask.html`** - Main web interface
  - Team selection dropdowns
  - Prediction display
  - Confidence badges
  - Factor explanations

### Static (`static/`)
- CSS stylesheets (if any)
- JavaScript files (if any)
- Images and assets

### Notebooks (`notebooks/`)
- Deployment demonstrations

##  Deliverables
-  Flask web application
-  Interactive user interface
-  Real-time predictions
-  Confidence levels displayed
-  Auto web scraping on startup
-  Responsive design

##  Application Features

### 1. Enhanced Multi-Factor Predictor
**5-Factor Weighted Model**:
- **FIFA Rank** (25%) - Current standing
- **FIFA Score** (35%) - Ranking points
- **Total Points** (20%) - Accumulated points
- **Confederation** (15%) - Regional advantage
- **Qualification Status** (5%) - Current status

### 2. Prediction Output
- **Win Probabilities**: Team A vs Team B percentages
- **Predicted Winner**: Clear winner indication
- **Confidence Level**: High/Medium/Low badges
- **Explanation**: Detailed factor breakdown
- **Factor Contributions**: Visual breakdown

### 3. Data Integration
- **Auto Web Scraping**: Loads latest FIFA 26 player data on startup
- **18,405 Players**: Complete database
- **45 Teams**: Squad statistics calculated
- **Real-time Updates**: Refresh data on demand

##  How to Run

### Option 1: Using run_app.py (Recommended)
```bash
# From project root
python run_app.py
```

### Option 2: Direct Flask
```bash
cd TASK_6_Deployment/app
python app_flask.py
```

### Access Application
Open browser: **http://localhost:5000**

##  Application Architecture

```
Browser Request
    ↓
Flask Server (app_flask.py)
    ↓
Data Loader (data_loader.py)
    → FIFA Rankings
    → Player Database (18,405 players)
    → Squad Statistics
    ↓
Enhanced Predictor (enhanced_predictor.py)
    → 5-Factor Analysis
    → Confidence Calculation
    → Explanation Generation
    ↓
HTML Response (index_flask.html)
```

##  User Interface

### Input Section
- Team A dropdown (all qualified teams)
- Team B dropdown (all qualified teams)
- "Predict Match" button
- "Refresh Data" button (reload player data)

### Output Section
- **Team A Probability**: Percentage with progress bar
- **Team B Probability**: Percentage with progress bar
- **Predicted Winner**: Highlighted with badge
- **Confidence**: High/Medium/Low indicator
- **Explanation**: Why this prediction was made
- **Factor Breakdown**: Contribution of each factor

### Confidence Levels
-  **High**: >70% probability difference
-  **Medium**: 55-70% probability difference
-  **Low**: <55% probability difference

##  Prediction Examples

### Example 1: Argentina vs Peru
```
Argentina: 78.5% 
Peru: 21.5%
Winner: Argentina
Confidence: HIGH

Explanation:
- Argentina ranks #1 (FIFA rank advantage)
- 1867 FIFA points vs 1590 (significant gap)
- CONMEBOL derby (home advantage)
- World Cup champions (experience)
```

### Example 2: Netherlands vs England
```
Netherlands: 52.3%
England: 47.7%
Winner: Netherlands
Confidence: LOW

Explanation:
- Close match (both UEFA powerhouses)
- Similar FIFA points (1854 vs 1849)
- Both top-10 ranked teams
- Experience roughly equal
```

##  Technical Stack
- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, Bootstrap
- **Data**: Pandas, NumPy
- **ML Models**: Scikit-learn (optional integration)
- **Web Scraping**: Custom scraper with Kaggle API

##  Deployment Notes

### Local Deployment (Current)
- Runs on localhost:5000
- Development server
- Auto-reload enabled

### Production Deployment (Future)
- Use Gunicorn/uWSGI
- Nginx reverse proxy
- SSL certificate
- Cloud hosting (AWS/Azure/GCP)

##  Performance
- **Load Time**: <2 seconds
- **Prediction Time**: <1 second
- **Data Refresh**: ~30 seconds (18,405 players)
- **Concurrent Users**: Development mode (1-2 users)

##  Documentation
See `../documentation/weekly_reports/Week3_Evaluation.md` for deployment details.

##  Future Enhancements
- Add ML model predictions (integrate .pkl files)
- Historical match comparisons
- Head-to-head statistics
- Mobile responsive design
- API endpoints for external access
- Real-time FIFA ranking updates
