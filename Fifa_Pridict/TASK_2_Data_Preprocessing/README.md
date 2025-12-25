# TASK 2: Data Preprocessing (15 Marks)

##  Objective
Clean, preprocess, and prepare data for machine learning model training.

##  Contents

### Scripts (`scripts/`)
- **`data_preprocessing.py`** - Comprehensive preprocessing pipeline
  - Data loading and validation
  - Feature engineering
  - Missing value handling
  - Outlier treatment
  - Feature selection
  - Data scaling

### Data (`data/`)
- **`processed/`** - Cleaned and preprocessed datasets
  - `top100_plus_qualified_master_dataset.csv` - Master training dataset
  - Feature-engineered data files
  - Scaled and normalized datasets
- **`cleaned/`** - Intermediate cleaned data

### Notebooks (`notebooks/`)
- Jupyter notebooks for preprocessing demonstrations

### Outputs (`outputs/`)
- Data quality reports
- Preprocessing summaries
- Feature statistics

##  Deliverables
-  Data cleaning pipeline
-  Feature engineering (6 new features created)
-  Missing value imputation (0% missing)
-  Outlier handling
-  Feature selection (15 best features)
-  Master dataset ready for ML

##  Preprocessing Steps

### 1. Data Cleaning
- Remove duplicates
- Handle missing values
- Standardize team names
- Fix data type inconsistencies

### 2. Feature Engineering
Created features:
- `team_strength` = total_points × experience_factor × avg_overall
- `form_category` = categorized point changes
- `experience_quality_ratio` = wc_experience / avg_overall
- `goal_scoring_efficiency` = wc_total_goals / wc_tournaments
- `team_balance` = std deviation of player attributes
- `continental_strength` = confederation-based multiplier

### 3. Feature Selection
- SelectKBest with k=15
- Removed highly correlated features
- Selected most predictive features

### 4. Data Scaling
- StandardScaler normalization
- Mean=0, Std=1 for all features

##  Data Quality Metrics
- **Missing Values**: 0%
- **Duplicates Removed**: Yes
- **Outliers Treated**: Yes
- **Final Quality Score**: 98/100

##  How to Run

```bash
cd scripts
python data_preprocessing.py
```

##  Results
- **Input**: 100 teams, 35 original features
- **Output**: 100 teams, 15 optimized features
- **Train/Test Split**: 80/20
- **Ready for**: Logistic Regression & Random Forest

##  Documentation
See `../documentation/weekly_reports/Week1_Data_Collection.md` for detailed preprocessing report.
