#!/usr/bin/env python3
"""
FIFA World Cup 2026 Prediction - Task 2: Model Evaluation and Visualization
Comprehensive evaluation system with visualizations and detailed analysis

This module provides:
- Performance metrics visualization
- ROC curves and precision-recall curves
- Feature importance plots
- Model comparison dashboards
- Detailed evaluation reports
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix, roc_curve, precision_recall_curve,
    roc_auc_score, average_precision_score
)
import warnings
warnings.filterwarnings('ignore')

class FIFAModelEvaluator:
    """
    Comprehensive model evaluation and visualization system
    """
    
    def __init__(self, results, figsize=(12, 8)):
        """
        Initialize the evaluator with classification results
        
        Args:
            results (dict): Results from FIFAClassificationModels
            figsize (tuple): Default figure size for plots
        """
        self.results = results
        self.figsize = figsize
        
        # Set plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        print(" FIFA Model Evaluator Initialized")
        print(f" Models available: {list(results.get('models', {}).keys())}")
    
    def plot_confusion_matrices(self, y_test, save_path="plots/confusion_matrices.png"):
        """
        Plot confusion matrices for all models
        
        Args:
            y_test (pd.Series): True test labels
            save_path (str): Path to save the plot
        """
        print("\\n Plotting confusion matrices...")
        
        models = list(self.results['models'].keys())
        n_models = len(models)
        
        fig, axes = plt.subplots(1, n_models, figsize=(6*n_models, 5))
        if n_models == 1:
            axes = [axes]
        
        for idx, model_name in enumerate(models):
            y_pred = self.results['predictions'][model_name]['y_pred']
            cm = confusion_matrix(y_test, y_pred)
            
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                       xticklabels=['Not Qualified', 'Qualified'],
                       yticklabels=['Not Qualified', 'Qualified'],
                       ax=axes[idx])
            
            axes[idx].set_title(f'{model_name.replace("_", " ").title()}\\nConfusion Matrix')
            axes[idx].set_xlabel('Predicted')
            axes[idx].set_ylabel('Actual')
        
        plt.tight_layout()
        
        # Save plot
        import os
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"    Saved: {save_path}")
        
        plt.show()
    
    def plot_roc_curves(self, y_test, save_path="plots/roc_curves.png"):
        """
        Plot ROC curves for all models
        
        Args:
            y_test (pd.Series): True test labels
            save_path (str): Path to save the plot
        """
        print("\\n Plotting ROC curves...")
        
        plt.figure(figsize=self.figsize)
        
        for model_name in self.results['models'].keys():
            if 'y_prob' in self.results['predictions'][model_name]:
                y_prob = self.results['predictions'][model_name]['y_prob']
                
                fpr, tpr, _ = roc_curve(y_test, y_prob)
                auc_score = roc_auc_score(y_test, y_prob)
                
                plt.plot(fpr, tpr, linewidth=2, 
                        label=f'{model_name.replace("_", " ").title()} (AUC = {auc_score:.3f})')
        
        plt.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random Classifier')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curves - FIFA 2026 Qualification Prediction')
        plt.legend(loc="lower right")
        plt.grid(True, alpha=0.3)
        
        # Save plot
        import os
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"    Saved: {save_path}")
        
        plt.show()
    
    def plot_precision_recall_curves(self, y_test, save_path="plots/precision_recall_curves.png"):
        """
        Plot precision-recall curves for all models
        
        Args:
            y_test (pd.Series): True test labels
            save_path (str): Path to save the plot
        """
        print("\\n Plotting precision-recall curves...")
        
        plt.figure(figsize=self.figsize)
        
        for model_name in self.results['models'].keys():
            if 'y_prob' in self.results['predictions'][model_name]:
                y_prob = self.results['predictions'][model_name]['y_prob']
                
                precision, recall, _ = precision_recall_curves(y_test, y_prob)
                ap_score = average_precision_score(y_test, y_prob)
                
                plt.plot(recall, precision, linewidth=2,
                        label=f'{model_name.replace("_", " ").title()} (AP = {ap_score:.3f})')
        
        # Baseline (random classifier)
        baseline = y_test.sum() / len(y_test)
        plt.axhline(y=baseline, color='k', linestyle='--', linewidth=1, 
                   label=f'Baseline (AP = {baseline:.3f})')
        
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Precision-Recall Curves - FIFA 2026 Qualification Prediction')
        plt.legend(loc="lower left")
        plt.grid(True, alpha=0.3)
        
        # Save plot
        import os
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"    Saved: {save_path}")
        
        plt.show()
    
    def plot_feature_importance(self, top_k=15, save_path="plots/feature_importance.png"):
        """
        Plot feature importance for all applicable models
        
        Args:
            top_k (int): Number of top features to display
            save_path (str): Path to save the plot
        """
        print(f"\\n Plotting feature importance (top {top_k})...")
        
        importance_data = self.results.get('feature_importance', {})
        
        if not importance_data:
            print("    No feature importance data available")
            return
        
        n_models = len(importance_data)
        fig, axes = plt.subplots(1, n_models, figsize=(8*n_models, 8))
        if n_models == 1:
            axes = [axes]
        
        for idx, (model_name, importance_df) in enumerate(importance_data.items()):
            top_features = importance_df.head(top_k)
            
            sns.barplot(data=top_features, y='feature', x='importance', ax=axes[idx])
            axes[idx].set_title(f'{model_name.replace("_", " ").title()}\\nTop {top_k} Features')
            axes[idx].set_xlabel('Importance Score')
            axes[idx].set_ylabel('Features')
        
        plt.tight_layout()
        
        # Save plot
        import os
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"    Saved: {save_path}")
        
        plt.show()
    
    def plot_cv_scores_comparison(self, save_path="plots/cv_scores_comparison.png"):
        """
        Plot cross-validation scores comparison
        
        Args:
            save_path (str): Path to save the plot
        """
        print("\\n Plotting cross-validation scores comparison...")
        
        cv_scores = self.results.get('cv_scores', {})
        
        if not cv_scores:
            print("    No cross-validation scores available")
            return
        
        # Prepare data for plotting
        plot_data = []
        for model_name, scores in cv_scores.items():
            for metric, metric_data in scores.items():
                plot_data.append({
                    'Model': model_name.replace('_', ' ').title(),
                    'Metric': metric.upper(),
                    'Mean_Score': metric_data['mean'],
                    'Std_Score': metric_data['std']
                })
        
        df_plot = pd.DataFrame(plot_data)
        
        # Create grouped bar plot
        plt.figure(figsize=(14, 8))
        
        metrics = df_plot['Metric'].unique()
        n_metrics = len(metrics)
        
        for i, metric in enumerate(metrics):
            plt.subplot(2, 3, i+1)
            metric_data = df_plot[df_plot['Metric'] == metric]
            
            bars = plt.bar(metric_data['Model'], metric_data['Mean_Score'], 
                          yerr=metric_data['Std_Score'], capsize=5)
            
            plt.title(f'{metric} Scores')
            plt.ylabel('Score')
            plt.xticks(rotation=45)
            plt.ylim(0, 1)
            
            # Add value labels on bars
            for bar, mean_val in zip(bars, metric_data['Mean_Score']):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                        f'{mean_val:.3f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        # Save plot
        import os
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"    Saved: {save_path}")
        
        plt.show()
    
    def create_model_comparison_table(self, save_path="plots/model_comparison_table.png"):
        """
        Create a comprehensive model comparison table
        
        Args:
            save_path (str): Path to save the plot
        """
        print("\\n Creating model comparison table...")
        
        # Get test evaluation results
        test_eval = self.results.get('test_evaluation', {})
        cv_scores = self.results.get('cv_scores', {})
        
        if not test_eval and not cv_scores:
            print("    No evaluation results available")
            return
        
        # Prepare comparison data
        comparison_data = []
        
        for model_name in self.results['models'].keys():
            row = {'Model': model_name.replace('_', ' ').title()}
            
            # Add test scores
            if model_name in test_eval:
                for metric, value in test_eval[model_name].items():
                    row[f'Test {metric.capitalize()}'] = f"{value:.4f}"
            
            # Add CV scores (mean ± std)
            if model_name in cv_scores:
                for metric, metric_data in cv_scores[model_name].items():
                    mean_val = metric_data['mean']
                    std_val = metric_data['std']
                    row[f'CV {metric.capitalize()}'] = f"{mean_val:.4f} ± {std_val:.4f}"
            
            comparison_data.append(row)
        
        df_comparison = pd.DataFrame(comparison_data)
        
        # Create table plot
        fig, ax = plt.subplots(figsize=(16, 6))
        ax.axis('tight')
        ax.axis('off')
        
        table = ax.table(cellText=df_comparison.values,
                        colLabels=df_comparison.columns,
                        cellLoc='center',
                        loc='center')
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        
        # Style the table
        for i in range(len(df_comparison.columns)):
            table[(0, i)].set_facecolor('#40466e')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        plt.title('FIFA 2026 World Cup Qualification Prediction - Model Comparison', 
                 fontsize=14, fontweight='bold', pad=20)
        
        # Save plot
        import os
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"    Saved: {save_path}")
        
        plt.show()
        
        return df_comparison
    
    def generate_detailed_report(self, y_test, save_path="reports/detailed_evaluation_report.txt"):
        """
        Generate a detailed text report of model evaluation
        
        Args:
            y_test (pd.Series): True test labels
            save_path (str): Path to save the report
        """
        print("\\n Generating detailed evaluation report...")
        
        import os
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'w') as f:
            f.write("FIFA 2026 WORLD CUP QUALIFICATION PREDICTION\\n")
            f.write("DETAILED MODEL EVALUATION REPORT\\n")
            f.write("=" * 80 + "\\n\\n")
            
            # Dataset Summary
            f.write("DATASET SUMMARY\\n")
            f.write("-" * 40 + "\\n")
            f.write(f"Total test samples: {len(y_test)}\\n")
            f.write(f"Qualified teams: {y_test.sum()} ({y_test.mean()*100:.1f}%)\\n")
            f.write(f"Non-qualified teams: {len(y_test) - y_test.sum()} ({(1-y_test.mean())*100:.1f}%)\\n\\n")
            
            # Model Performance
            test_eval = self.results.get('test_evaluation', {})
            
            for model_name, metrics in test_eval.items():
                f.write(f"{model_name.upper().replace('_', ' ')} PERFORMANCE\\n")
                f.write("-" * 40 + "\\n")
                
                for metric, value in metrics.items():
                    f.write(f"{metric.capitalize()}: {value:.4f}\\n")
                
                # Add predictions summary
                predictions = self.results['predictions'][model_name]
                y_pred = predictions['y_pred']
                
                correct_predictions = (y_test == y_pred).sum()
                f.write(f"Correct predictions: {correct_predictions}/{len(y_test)}\\n")
                
                # True/False positives and negatives
                from sklearn.metrics import confusion_matrix
                tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
                f.write(f"True Positives: {tp}\\n")
                f.write(f"True Negatives: {tn}\\n")
                f.write(f"False Positives: {fp}\\n")
                f.write(f"False Negatives: {fn}\\n\\n")
            
            # Feature Importance
            feature_importance = self.results.get('feature_importance', {})
            if feature_importance:
                f.write("FEATURE IMPORTANCE ANALYSIS\\n")
                f.write("-" * 40 + "\\n")
                
                for model_name, importance_df in feature_importance.items():
                    f.write(f"\\n{model_name.upper().replace('_', ' ')} - Top 10 Features:\\n")
                    for idx, row in importance_df.head(10).iterrows():
                        f.write(f"  {row['feature']}: {row['importance']:.4f}\\n")
            
            # Best Parameters
            best_params = self.results.get('best_parameters', {})
            if best_params:
                f.write("\\nOPTIMAL HYPERPARAMETERS\\n")
                f.write("-" * 40 + "\\n")
                
                for model_name, params in best_params.items():
                    f.write(f"\\n{model_name.upper().replace('_', ' ')}:\\n")
                    for param, value in params.items():
                        f.write(f"  {param}: {value}\\n")
            
            f.write("\\n" + "=" * 80 + "\\n")
            f.write("Report generated by FIFA Model Evaluator\\n")
        
        print(f"    Saved: {save_path}")
    
    def create_comprehensive_dashboard(self, y_test, save_all_plots=True):
        """
        Create a comprehensive evaluation dashboard
        
        Args:
            y_test (pd.Series): True test labels
            save_all_plots (bool): Whether to save all individual plots
        """
        print("\\n Creating comprehensive evaluation dashboard...")
        print("=" * 60)
        
        if save_all_plots:
            # Individual plots
            self.plot_confusion_matrices(y_test)
            self.plot_roc_curves(y_test)
            self.plot_precision_recall_curves(y_test)
            self.plot_feature_importance()
            self.plot_cv_scores_comparison()
            comparison_table = self.create_model_comparison_table()
            
            # Detailed report
            self.generate_detailed_report(y_test)
        
        print("\\n" + "=" * 60)
        print(" Comprehensive evaluation dashboard completed!")
        print(" Check the 'plots' and 'reports' directories for all outputs")
        print("=" * 60)
        
        return True

def run_fifa_evaluation():
    """
    Main function to run complete FIFA model evaluation
    """
    print(" FIFA 2026 Model Evaluation System")
    print("=" * 50)
    
    try:
        # Import and run classification
        import sys
        import os
        classification_path = os.path.join(os.path.dirname(__file__), "..", "..", "TASK_3_Model_Building", "scripts")
        sys.path.insert(0, classification_path)
        from fifa_classification_models import run_fifa_classification
        
        # Get classification results
        results = run_fifa_classification()
        
        if results is None:
            print(" Classification failed. Cannot proceed with evaluation.")
            return None
        
        # Extract test data for evaluation
        import sys
        import os
        preprocessing_path = os.path.join(os.path.dirname(__file__), "..", "..", "TASK_2_Data_Preprocessing", "scripts")
        sys.path.insert(0, preprocessing_path)
        from data_preprocessing import FIFADataPreprocessor
        
        # Use correct data path
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "TASK_2_Data_Preprocessing", "data", "processed", "top100_plus_qualified_master_dataset.csv")
        preprocessor = FIFADataPreprocessor(data_path=data_path)
        preprocessing_results = preprocessor.run_complete_preprocessing()
        y_test = preprocessing_results['y_test']
        
        # Initialize evaluator and create dashboard
        evaluator = FIFAModelEvaluator(results)
        evaluator.create_comprehensive_dashboard(y_test, save_all_plots=True)
        
        return evaluator
        
    except Exception as e:
        print(f" Evaluation failed: {e}")
        return None

if __name__ == "__main__":
    evaluator = run_fifa_evaluation()
    
    if evaluator:
        print("\\n FIFA model evaluation completed successfully!")
    else:
        print("\\n FIFA model evaluation failed")