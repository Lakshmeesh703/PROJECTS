# TASK 3: Model Building & Training (25 Marks)

##  Objective
Build, train, and optimize machine learning models for FIFA World Cup 2026 qualification prediction.

##  Contents

### Scripts (`scripts/`)
- **`train_logistic_regression.py`** - Logistic Regression training (standalone)
- **`train_random_forest.py`** - Random Forest training (standalone)
- **`fifa_classification_models.py`** - Complete training pipeline with hyperparameter tuning

### Models (`models/`)
- **`logistic_regression_fifa_2026.pkl`** - Trained Logistic Regression model
- **`random_forest_fifa_2026.pkl`** - Trained Random Forest model
- **`model_results.pkl`** - Model metadata and results

### Notebooks (`notebooks/`)
- Jupyter notebooks for model training demonstrations

### Outputs (`outputs/`)
- Training logs
- Model performance reports
- Hyperparameter tuning results

##  Deliverables
-  2 trained classification models
-  Hyperparameter tuning implemented
-  Cross-validation performed
-  Models saved as .pkl files (Python 3.13 compatible)
-  Training performance documented

##  Models Implemented

### 1. Logistic Regression
**Parameters**:
- C = 1.0
- solver = 'lbfgs'
- max_iter = 1000

**Performance**:
- Training Accuracy: 81.25%
- Test Accuracy: 60.00%

**Features**: 13 selected features

### 2. Random Forest
**Parameters**:
- n_estimators = 100
- max_depth = 10
- min_samples_split = 5
- min_samples_leaf = 2
- random_state = 42

**Performance**:
- Training Accuracy: 97.50%
- Test Accuracy: 70.00%

**Features**: 13 selected features
**Top Features by Importance**:
1. avg_pace: 17.10%
2. total.points: 13.23%
3. rank: 11.50%
4. previous.points: 10.52%
5. avg_defending: 7.87%

##  How to Run

### Train Individual Models

**Logistic Regression**:
```bash
cd scripts
python train_logistic_regression.py
```

**Random Forest**:
```bash
cd scripts
python train_random_forest.py
```

### Train All Models with Hyperparameter Tuning
```bash
cd ../..
python TASK_3_Model_Building/scripts/fifa_classification_models.py
```

##  Training Configuration
- **Dataset**: 100 teams
- **Features**: 15 (after SelectKBest)
- **Train/Test Split**: 80/20 (stratified)
- **Cross-Validation**: 5-fold StratifiedKFold
- **Scoring Metric**: ROC-AUC
- **Random State**: 42 (reproducible)

##  Model Selection Criteria
- Test accuracy
- Cross-validation stability
- Generalization ability
- Training time
- Interpretability

**Selected Model**: Random Forest (70% test accuracy, better generalization)

##  Documentation
See `../documentation/weekly_reports/Week2_Model_Training.md` for detailed training report.
