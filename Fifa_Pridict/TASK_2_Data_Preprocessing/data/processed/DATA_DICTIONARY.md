# FIFA 2026 World Cup Prediction - Data Dictionary

## Master Dataset: `top100_plus_qualified_master_dataset.csv`

This cleaned dataset contains comprehensive features for FIFA World Cup 2026 prediction analysis.

---

##  Column Descriptions

### **Identification Columns**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `date` | Date | Date of data collection | 2024 |
| `semester` | Integer | Semester of the year (1 or 2) | 2 |
| `rank` | Integer | FIFA world ranking position | 1 |
| `team_name` | String | Official team/country name | Argentina |
| `acronym` | String | FIFA 3-letter country code | ARG |
| `confederation` | String | FIFA confederation (CONMEBOL, UEFA, CAF, AFC, CONCACAF, OFC) | CONMEBOL |

---

### **FIFA Ranking Features**

| Column | Type | Description | Range/Unit |
|--------|------|-------------|------------|
| `total.points` | Float | Current FIFA ranking points | 0 - 2000+ |
| `previous.points` | Float | Previous period FIFA points | 0 - 2000+ |
| `diff.points` | Float | Change in FIFA points (current - previous) | -500 to +500 |
| `points_momentum` | Float | Point change momentum indicator | Same as diff.points |

---

### **Qualification Status**

| Column | Type | Description | Values |
|--------|------|-------------|--------|
| `qualified_2026` | Binary | FIFA 2026 World Cup qualification status | 0 = Not qualified, 1 = Qualified |

---

### **Goal Statistics Features**

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `total_goals` | Integer | Total goals scored by team | Historical data |
| `penalty_goals` | Integer | Goals scored from penalties | Subset of total_goals |
| `own_goals` | Integer | Own goals scored against opponents | Not included in total_goals |
| `clean_goals` | Integer | Goals scored from open play (excluding penalties) | total_goals - penalty_goals |

---

### **Squad Quality Features** 
*(Derived from FIFA player database)*

| Column | Type | Description | Range |
|--------|------|-------------|-------|
| `avg_overall` | Float | Average overall player rating | 0 - 100 |
| `max_overall` | Integer | Highest player rating in squad | 0 - 100 |
| `squad_size` | Integer | Total number of players in national team pool | 50 - 2000+ |
| `avg_potential` | Float | Average player potential rating | 0 - 100 |
| `avg_age` | Float | Average squad age in years | 18 - 35 |

---

### **Player Attribute Averages**
*(From FIFA player ratings)*

| Column | Type | Description | Range |
|--------|------|-------------|-------|
| `avg_pace` | Float | Average pace/speed rating | 0 - 100 |
| `avg_shooting` | Float | Average shooting ability rating | 0 - 100 |
| `avg_passing` | Float | Average passing accuracy rating | 0 - 100 |
| `avg_dribbling` | Float | Average dribbling skill rating | 0 - 100 |
| `avg_defending` | Float | Average defensive ability rating | 0 - 100 |
| `avg_physic` | Float | Average physical strength rating | 0 - 100 |

---

### **World Cup Experience Features**

| Column | Type | Description | Calculation |
|--------|------|-------------|-------------|
| `wc_total_goals` | Integer | Total goals scored in World Cup history | Sum of all WC goals |
| `wc_tournaments` | Integer | Number of World Cup tournaments participated | Count of appearances |
| `wc_experience_score` | Float | Composite World Cup experience metric | wc_total_goals * wc_tournaments |

---

### **Engineered Performance Features**

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `squad_quality` | Float | Overall squad quality rating | (avg_overall + avg_potential) / 2 |
| `attack_rating` | Float | Offensive capability rating | (avg_shooting + avg_passing + avg_dribbling) / 3 |
| `defense_rating` | Float | Defensive capability rating | (avg_defending + avg_physic) / 2 |
| `goal_efficiency` | Float | Goal scoring efficiency | total_goals / squad_size |
| `experience_factor` | Float | Normalized World Cup experience | wc_tournaments / max(wc_tournaments) |
| `qualification_probability` | Float | Predicted qualification likelihood | Model-based probability (0-1) |

---

##  Target Variable

**Primary Target:** `qualified_2026` (Binary classification)
- **0**: Team has NOT qualified for FIFA 2026 World Cup
- **1**: Team HAS qualified for FIFA 2026 World Cup

**Alternative Targets** (for different prediction tasks):
- `qualification_probability`: Probability of qualification (Regression)
- `rank`: FIFA ranking prediction (Regression/Ordinal)

---

##  Data Quality Metrics

| Metric | Value |
|--------|-------|
| **Total Records** | 102 teams |
| **Total Features** | 35+ columns |
| **Missing Values** | Cleaned (imputed/removed) |
| **Duplicates** | Removed |
| **Date Range** | Current as of October 2025 |
| **Geographic Coverage** | All 6 FIFA confederations |

---

##  Feature Categories Summary

1. **Identification** (6 features): Basic team information
2. **FIFA Ranking** (4 features): Official FIFA ranking metrics
3. **Qualification** (1 feature): Target variable
4. **Goal Statistics** (4 features): Scoring performance
5. **Squad Quality** (5 features): Team strength indicators
6. **Player Attributes** (6 features): Average player ratings
7. **World Cup History** (3 features): Tournament experience
8. **Engineered Features** (6 features): Derived performance metrics

---

##  Data Sources

1. **FIFA Rankings**: Official FIFA world rankings (fifa.com)
2. **Match Results**: International football results database
3. **Player Statistics**: FIFA 26 player database (Kaggle dataset)
4. **World Cup History**: Historical World Cup goals and participation
5. **Qualification Status**: FIFA 2026 World Cup qualification tracker

---

##  Data Cleaning Steps Applied

1.  **Duplicate Removal**: Removed duplicate team records
2.  **Missing Value Handling**: 
   - Imputed numerical values with median
   - Filled categorical values with mode
   - Removed records with >50% missing data
3.  **Outlier Treatment**: Capped extreme values using IQR method
4.  **Data Type Validation**: Ensured correct dtypes for all columns
5.  **Standardization**: Normalized team names and confederations
6.  **Feature Engineering**: Created derived metrics from raw data

---

##  Usage Examples

### Load the dataset:
```python
import pandas as pd

# Load master dataset
df = pd.read_csv('data/processed/top100_plus_qualified_master_dataset.csv')

# Display basic info
print(f"Total teams: {len(df)}")
print(f"Qualified teams: {df['qualified_2026'].sum()}")
print(f"Features: {len(df.columns)}")
```

### Feature selection for ML:
```python
# Select numerical features for modeling
feature_columns = [
    'total.points', 'avg_overall', 'avg_age', 'avg_pace',
    'avg_shooting', 'avg_passing', 'avg_dribbling', 
    'avg_defending', 'wc_experience_score', 'squad_quality',
    'attack_rating', 'defense_rating', 'goal_efficiency'
]

X = df[feature_columns]
y = df['qualified_2026']
```

---

##  Statistical Summary

| Feature Type | Count | Mean Range | Std Range |
|--------------|-------|------------|-----------|
| FIFA Points | 4 | 800 - 1800 | 200 - 400 |
| Squad Ratings | 11 | 50 - 75 | 5 - 15 |
| WC Experience | 3 | 50 - 400 | 100 - 200 |
| Engineered | 6 | 0.5 - 70 | 0.2 - 20 |

---

**Data Dictionary Version:** 1.0  
**Last Updated:** October 25, 2025  
**Contact:** FIFA Prediction Team
