# TASK 4: Model Evaluation (15 Marks)

##  Objective
Evaluate model performance using comprehensive metrics and visualizations.

##  Contents

### Scripts (`scripts/`)
- **`fifa_model_evaluation.py`** - Complete evaluation pipeline
- **`test_models.py`** - Model loading and validation tests

### Plots (`plots/`)
- Confusion matrices
- ROC curves
- Precision-Recall curves
- Performance comparison charts
- Cross-validation score distributions

### Notebooks (`notebooks/`)
- Jupyter notebooks for evaluation demonstrations

### Outputs (`outputs/`)
- Evaluation reports
- Performance metrics summaries
- Model comparison tables

##  Deliverables
-  Accuracy, Precision, Recall, F1-score metrics
-  ROC-AUC curves
-  Confusion matrices
-  Model comparison analysis
-  Performance visualizations
-  Critical evaluation report

##  Evaluation Metrics

### Logistic Regression Performance
- **Test Accuracy**: 60.00%
- **Precision**: TBD
- **Recall**: TBD
- **F1-Score**: TBD
- **ROC-AUC**: TBD

### Random Forest Performance
- **Test Accuracy**: 70.00%
- **Precision**: TBD
- **Recall**: TBD
- **F1-Score**: TBD
- **ROC-AUC**: TBD

### Cross-Validation Results
- 5-fold stratified CV
- Mean CV score
- Standard deviation
- Consistency across folds

##  Visualizations Generated

### 1. Confusion Matrices
- True Positives / False Positives
- True Negatives / False Negatives
- Per-class accuracy

### 2. ROC Curves
- True Positive Rate vs False Positive Rate
- Area Under Curve (AUC)
- Model comparison on same plot

### 3. Precision-Recall Curves
- Precision vs Recall trade-off
- Average Precision score
- Optimal threshold identification

### 4. Performance Comparison
- Side-by-side metric comparison
- Bar charts for each metric
- Statistical significance tests

### 5. Cross-Validation Scores
- Distribution plots
- Confidence intervals
- Stability assessment

##  How to Run

### Run Complete Evaluation
```bash
cd scripts
python fifa_model_evaluation.py
```

### Test Model Loading
```bash
python test_models.py
```

##  Model Comparison

| Metric | Logistic Regression | Random Forest | Winner |
|--------|-------------------|---------------|---------|
| Test Accuracy | 60.00% | **70.00%** | RF  |
| Training Time | Fast | Moderate | LR  |
| Interpretability | High | Moderate | LR  |
| Generalization | Good | **Better** | RF  |

**Recommendation**: Random Forest for deployment (better accuracy and generalization)

##  Strengths & Weaknesses

### Logistic Regression
**Strengths**:
- Fast training
- Highly interpretable coefficients
- Works well with linear relationships
- Low computational requirements

**Weaknesses**:
- Lower accuracy (60%)
- Assumes linear decision boundaries
- May miss complex patterns

### Random Forest
**Strengths**:
- Higher accuracy (70%)
- Captures non-linear patterns
- Robust to outliers
- Provides feature importance

**Weaknesses**:
- Slower training
- Less interpretable
- Prone to overfitting (97.5% train vs 70% test)

##  Documentation
See `../documentation/weekly_reports/Week3_Evaluation.md` for detailed evaluation report.
