#!/usr/bin/env python3
"""
FIFA World Cup 2026 Prediction - Task 2: Classification Models
Implementation of Logistic Regression and Random Forest models

This module provides:
- Logistic Regression classifier with hyperparameter tuning
- Random Forest classifier with hyperparameter tuning  
- Cross-validation and model evaluation
- Feature importance analysis
- Model comparison and performance metrics
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, 
    roc_curve, precision_recall_curve, accuracy_score, 
    precision_score, recall_score, f1_score
)
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import warnings
warnings.filterwarnings('ignore')

class FIFAClassificationModels:
    """
    Classification models for predicting FIFA World Cup qualification
    """
    
    def __init__(self, random_state=42):
        """
        Initialize the classification models
        
        Args:
            random_state (int): Random seed for reproducibility
        """
        self.random_state = random_state
        self.models = {}
        self.best_params = {}
        self.cv_scores = {}
        self.predictions = {}
        self.feature_importance = {}
        
        print(" FIFA Classification Models Initialized")
        print(f" Random state: {random_state}")
    
    def initialize_models(self):
        """
        Initialize base models with default parameters
        """
        print("\n Initializing base models...")
        
        # Logistic Regression
        self.models['logistic_regression'] = LogisticRegression(
            random_state=self.random_state,
            max_iter=1000,
            solver='liblinear'  # Good for small datasets
        )
        
        # Random Forest
        self.models['random_forest'] = RandomForestClassifier(
            random_state=self.random_state,
            n_estimators=100,
            max_depth=None,
            min_samples_split=2,
            min_samples_leaf=1
        )
        
        print(f"    Initialized {len(self.models)} models:")
        for name in self.models.keys():
            print(f"      • {name}")
    
    def define_hyperparameter_grids(self):
        """
        Define hyperparameter grids for grid search
        
        Returns:
            dict: Hyperparameter grids for each model
        """
        param_grids = {
            'logistic_regression': {
                'C': [0.001, 0.01, 0.1, 1, 10, 100],
                'penalty': ['l1', 'l2'],
                'solver': ['liblinear'],
                'class_weight': [None, 'balanced']
            },
            'random_forest': {
                'n_estimators': [50, 100, 200],
                'max_depth': [3, 5, 7, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4],
                'class_weight': [None, 'balanced']
            }
        }
        
        print(" Hyperparameter grids defined:")
        for model_name, grid in param_grids.items():
            print(f"   • {model_name}: {len(grid)} parameters")
            
        return param_grids
    
    def perform_hyperparameter_tuning(self, X_train, y_train, cv_folds=5, scoring='roc_auc', n_jobs=-1):
        """
        Perform hyperparameter tuning using GridSearchCV
        
        Args:
            X_train (pd.DataFrame): Training features
            y_train (pd.Series): Training target
            cv_folds (int): Number of cross-validation folds
            scoring (str): Scoring metric for optimization
            n_jobs (int): Number of parallel jobs
            
        Returns:
            dict: Best parameters for each model
        """
        print(f"\n Hyperparameter tuning ({cv_folds}-fold CV, scoring='{scoring}')...")
        
        if not self.models:
            self.initialize_models()
        
        param_grids = self.define_hyperparameter_grids()
        
        for model_name, model in self.models.items():
            print(f"\n    Tuning {model_name}...")
            
            # Create GridSearchCV
            grid_search = GridSearchCV(
                estimator=model,
                param_grid=param_grids[model_name],
                cv=StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state),
                scoring=scoring,
                n_jobs=n_jobs,
                verbose=0
            )
            
            # Fit grid search
            grid_search.fit(X_train, y_train)
            
            # Store results
            self.best_params[model_name] = grid_search.best_params_
            self.models[model_name] = grid_search.best_estimator_
            
            print(f"       Best {scoring}: {grid_search.best_score_:.4f}")
            print(f"       Best params: {grid_search.best_params_}")
        
        print("\n Hyperparameter tuning completed!")
        return self.best_params
    
    def train_models(self, X_train, y_train, tune_hyperparameters=True):
        """
        Train all models with optional hyperparameter tuning
        
        Args:
            X_train (pd.DataFrame): Training features
            y_train (pd.Series): Training target
            tune_hyperparameters (bool): Whether to perform hyperparameter tuning
        """
        print(f"\n Training models (tune_hyperparameters={tune_hyperparameters})...")
        
        if tune_hyperparameters:
            self.perform_hyperparameter_tuning(X_train, y_train)
        else:
            if not self.models:
                self.initialize_models()
            
            # Train models with default parameters
            for model_name, model in self.models.items():
                print(f"    Training {model_name}...")
                model.fit(X_train, y_train)
                print(f"       {model_name} trained")
        
        print(" All models trained successfully!")
    
    def cross_validate_models(self, X_train, y_train, cv_folds=5, scoring=['accuracy', 'precision', 'recall', 'f1', 'roc_auc']):
        """
        Perform cross-validation on trained models
        
        Args:
            X_train (pd.DataFrame): Training features
            y_train (pd.Series): Training target
            cv_folds (int): Number of cross-validation folds
            scoring (list): List of scoring metrics
            
        Returns:
            dict: Cross-validation scores for each model
        """
        print(f"\n Cross-validation ({cv_folds}-fold)...")
        
        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state)
        
        for model_name, model in self.models.items():
            print(f"\\n    Cross-validating {model_name}...")
            
            model_scores = {}
            for metric in scoring:
                scores = cross_val_score(model, X_train, y_train, cv=cv, scoring=metric)
                model_scores[metric] = {
                    'mean': scores.mean(),
                    'std': scores.std(),
                    'scores': scores
                }
                print(f"      • {metric}: {scores.mean():.4f} (±{scores.std()*2:.4f})")
            
            self.cv_scores[model_name] = model_scores
        
        print(" Cross-validation completed!")
        return self.cv_scores
    
    def make_predictions(self, X_test, return_probabilities=True):
        """
        Make predictions on test set
        
        Args:
            X_test (pd.DataFrame): Test features
            return_probabilities (bool): Whether to return prediction probabilities
            
        Returns:
            dict: Predictions for each model
        """
        print("\\n Making predictions on test set...")
        
        for model_name, model in self.models.items():
            predictions = {
                'y_pred': model.predict(X_test),
                'y_pred_binary': model.predict(X_test)
            }
            
            if return_probabilities and hasattr(model, 'predict_proba'):
                predictions['y_prob'] = model.predict_proba(X_test)[:, 1]
            
            self.predictions[model_name] = predictions
            print(f"    {model_name}: {len(predictions['y_pred'])} predictions made")
        
        print(" Predictions completed!")
        return self.predictions
    
    def evaluate_models(self, y_test, detailed=True):
        """
        Evaluate model performance on test set
        
        Args:
            y_test (pd.Series): True test labels
            detailed (bool): Whether to show detailed evaluation
            
        Returns:
            dict: Evaluation metrics for each model
        """
        print("\\n Evaluating model performance...")
        
        evaluation_results = {}
        
        for model_name, predictions in self.predictions.items():
            y_pred = predictions['y_pred']
            y_prob = predictions.get('y_prob', None)
            
            # Calculate metrics
            metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, average='binary'),
                'recall': recall_score(y_test, y_pred, average='binary'),
                'f1': f1_score(y_test, y_pred, average='binary')
            }
            
            if y_prob is not None:
                metrics['roc_auc'] = roc_auc_score(y_test, y_prob)
            
            evaluation_results[model_name] = metrics
            
            # Print results
            print(f"\\n    {model_name.upper()}:")
            for metric, value in metrics.items():
                print(f"      • {metric.capitalize()}: {value:.4f}")
            
            if detailed:
                print(f"\n       Classification Report:")
                # sklearn's classification_report doesn't support 'prefix'; print raw report
                report = classification_report(
                    y_test, y_pred,
                    target_names=['Not Qualified', 'Qualified']
                )
                print(report)
        
        print(" Model evaluation completed!")
        return evaluation_results
    
    def analyze_feature_importance(self, feature_names, top_k=10):
        """
        Analyze and display feature importance for tree-based models
        
        Args:
            feature_names (list): List of feature names
            top_k (int): Number of top features to display
            
        Returns:
            dict: Feature importance for each applicable model
        """
        print(f"\\n Analyzing feature importance (top {top_k})...")
        
        for model_name, model in self.models.items():
            if hasattr(model, 'feature_importances_'):
                # Get feature importance
                importance = model.feature_importances_
                feature_importance_df = pd.DataFrame({
                    'feature': feature_names,
                    'importance': importance
                }).sort_values('importance', ascending=False)
                
                self.feature_importance[model_name] = feature_importance_df
                
                print(f"\\n    {model_name.upper()} - Top {top_k} Features:")
                for idx, row in feature_importance_df.head(top_k).iterrows():
                    print(f"      • {row['feature']}: {row['importance']:.4f}")
            
            elif hasattr(model, 'coef_'):
                # For logistic regression, use coefficient magnitudes
                importance = np.abs(model.coef_[0])
                feature_importance_df = pd.DataFrame({
                    'feature': feature_names,
                    'importance': importance
                }).sort_values('importance', ascending=False)
                
                self.feature_importance[model_name] = feature_importance_df
                
                print(f"\\n    {model_name.upper()} - Top {top_k} Features (by coefficient magnitude):")
                for idx, row in feature_importance_df.head(top_k).iterrows():
                    print(f"      • {row['feature']}: {row['importance']:.4f}")
        
        print(" Feature importance analysis completed!")
        return self.feature_importance
    
    def save_models(self, save_dir="models"):
        """
        Save trained models to disk
        
        Args:
            save_dir (str): Directory to save models
        """
        import os
        os.makedirs(save_dir, exist_ok=True)
        
        print(f"\\n Saving models to {save_dir}/...")
        
        for model_name, model in self.models.items():
            model_path = f"{save_dir}/{model_name}_fifa_2026.pkl"
            joblib.dump(model, model_path)
            print(f"    Saved: {model_path}")
        
        # Save additional results
        results_path = f"{save_dir}/model_results.pkl"
        results = {
            'best_params': self.best_params,
            'cv_scores': self.cv_scores,
            'feature_importance': self.feature_importance
        }
        joblib.dump(results, results_path)
        print(f"    Saved: {results_path}")
        
        print(" All models saved successfully!")
    
    def generate_model_comparison(self):
        """
        Generate a comprehensive comparison of all models
        
        Returns:
            pd.DataFrame: Model comparison summary
        """
        print("\\n Generating model comparison...")
        
        comparison_data = []
        
        for model_name in self.models.keys():
            row = {'Model': model_name}
            
            # Add CV scores if available
            if model_name in self.cv_scores:
                for metric in ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']:
                    if metric in self.cv_scores[model_name]:
                        row[f'CV_{metric}_mean'] = self.cv_scores[model_name][metric]['mean']
                        row[f'CV_{metric}_std'] = self.cv_scores[model_name][metric]['std']
            
            # Add test performance if available
            if hasattr(self, 'test_evaluation') and model_name in self.test_evaluation:
                for metric, value in self.test_evaluation[model_name].items():
                    row[f'Test_{metric}'] = value
            
            # Add best parameters if available
            if model_name in self.best_params:
                row['Best_Params'] = str(self.best_params[model_name])
            
            comparison_data.append(row)
        
        comparison_df = pd.DataFrame(comparison_data)
        
        print(" Model comparison generated!")
        return comparison_df
    
    def run_complete_classification(self, X_train, X_test, y_train, y_test, feature_names,
                                   tune_hyperparameters=True, perform_cv=True, save_models=True):
        """
        Run the complete classification pipeline
        
        Args:
            X_train, X_test: Training and test features
            y_train, y_test: Training and test targets
            feature_names: List of feature names
            tune_hyperparameters: Whether to tune hyperparameters
            perform_cv: Whether to perform cross-validation
            save_models: Whether to save trained models
            
        Returns:
            dict: Complete classification results
        """
        print(" Running complete classification pipeline...")
        print("=" * 70)
        
        # Step 1: Train models
        self.train_models(X_train, y_train, tune_hyperparameters=tune_hyperparameters)
        
        # Step 2: Cross-validation (optional)
        if perform_cv:
            self.cross_validate_models(X_train, y_train)
        
        # Step 3: Make predictions
        self.make_predictions(X_test)
        
        # Step 4: Evaluate models
        self.test_evaluation = self.evaluate_models(y_test)
        
        # Step 5: Analyze feature importance
        self.analyze_feature_importance(feature_names)
        
        # Step 6: Save models (optional)
        if save_models:
            self.save_models()
        
        # Step 7: Generate comparison
        comparison_df = self.generate_model_comparison()
        
        # Create results summary
        results = {
            'models': self.models,
            'best_parameters': self.best_params,
            'cv_scores': self.cv_scores,
            'test_evaluation': self.test_evaluation,
            'predictions': self.predictions,
            'feature_importance': self.feature_importance,
            'model_comparison': comparison_df
        }
        
        print("\\n" + "=" * 70)
        print(" Complete classification pipeline finished!")
        print(f" Models trained: {len(self.models)}")
        print(f" Evaluation metrics calculated")
        print(f" Feature importance analyzed")
        print("=" * 70)
        
        return results

def run_fifa_classification():
    """
    Main function to run FIFA classification with preprocessed data
    """
    print(" FIFA 2026 World Cup Qualification Prediction")
    print("=" * 50)
    
    # Import preprocessing
    import sys
    import os
    preprocessing_path = os.path.join(os.path.dirname(__file__), "..", "..", "TASK_2_Data_Preprocessing", "scripts")
    sys.path.insert(0, preprocessing_path)
    from data_preprocessing import FIFADataPreprocessor
    
    # Run preprocessing
    # Use correct path relative to project root
    data_path = os.path.join(os.path.dirname(__file__), "..", "..", "TASK_2_Data_Preprocessing", "data", "processed", "top100_plus_qualified_master_dataset.csv")
    preprocessor = FIFADataPreprocessor(data_path=data_path)
    preprocessing_results = preprocessor.run_complete_preprocessing()
    
    if preprocessing_results is None:
        print(" Preprocessing failed. Cannot proceed with classification.")
        return None
    
    # Extract preprocessed data
    X_train = preprocessing_results['X_train']
    X_test = preprocessing_results['X_test']
    y_train = preprocessing_results['y_train']
    y_test = preprocessing_results['y_test']
    feature_names = preprocessing_results['feature_names']
    
    # Initialize and run classification
    classifier = FIFAClassificationModels(random_state=42)
    classification_results = classifier.run_complete_classification(
        X_train, X_test, y_train, y_test, feature_names,
        tune_hyperparameters=True,
        perform_cv=True,
        save_models=True
    )
    
    return classification_results

if __name__ == "__main__":
    results = run_fifa_classification()
    
    if results:
        print("\\n FIFA classification completed successfully!")
        print(" Check the 'models' directory for saved models")
    else:
        print("\\n FIFA classification failed")