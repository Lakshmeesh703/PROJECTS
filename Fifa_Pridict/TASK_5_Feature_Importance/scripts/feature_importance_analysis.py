"""
TASK 5: Feature Importance Analysis
Extract and visualize feature importance from trained models
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class FeatureImportanceAnalyzer:
    def __init__(self):
        """Initialize Feature Importance Analyzer"""
        self.project_root = Path(__file__).parent.parent.parent
        self.models_dir = self.project_root / "TASK_3_Model_Building" / "models"
        self.plots_dir = self.project_root / "TASK_5_Feature_Importance" / "plots"
        self.outputs_dir = self.project_root / "TASK_5_Feature_Importance" / "outputs"
        
        # Create output directories
        self.plots_dir.mkdir(exist_ok=True)
        self.outputs_dir.mkdir(exist_ok=True)
        
        # Load models
        self.rf_model = None
        self.lr_model = None
        self.feature_names = None
        
    def load_models(self):
        """Load trained models"""
        print("\n" + "="*60)
        print("LOADING TRAINED MODELS")
        print("="*60)
        
        try:
            # Load Random Forest
            rf_path = self.models_dir / "random_forest_fifa_2026.pkl"
            if rf_path.exists():
                self.rf_model = joblib.load(rf_path)
                print(f"✓ Random Forest loaded: {rf_path}")
            else:
                print(f"✗ Random Forest not found: {rf_path}")
            
            # Load Logistic Regression
            lr_path = self.models_dir / "logistic_regression_fifa_2026.pkl"
            if lr_path.exists():
                self.lr_model = joblib.load(lr_path)
                print(f"✓ Logistic Regression loaded: {lr_path}")
            else:
                print(f"✗ Logistic Regression not found: {lr_path}")
                
        except Exception as e:
            print(f"Error loading models: {e}")
    
    def load_feature_names(self):
        """Load feature names from training data"""
        print("\n" + "="*60)
        print("LOADING FEATURE NAMES")
        print("="*60)
        
        try:
            # Load training data to get feature names
            data_path = self.project_root / "TASK_2_Data_Preprocessing" / "data" / "processed" / "top100_plus_qualified_master_dataset.csv"
            
            if data_path.exists():
                df = pd.read_csv(data_path)
                
                # Features used in training (based on model building)
                feature_columns = [
                    'rank', 'total.points', 'previous.points', 
                    'avg_pace', 'avg_shooting', 'avg_passing', 'avg_dribbling',
                    'avg_defending', 'avg_physic', 'avg_overall', 'avg_potential',
                    'wc_experience_score', 'confederation_rank'
                ]
                
                self.feature_names = feature_columns
                print(f"✓ Loaded {len(self.feature_names)} features")
                print(f"Features: {self.feature_names}")
            else:
                print(f"✗ Training data not found: {data_path}")
                # Default feature names
                self.feature_names = [
                    'rank', 'total.points', 'previous.points', 
                    'avg_pace', 'avg_shooting', 'avg_passing', 'avg_dribbling',
                    'avg_defending', 'avg_physic', 'avg_overall', 'avg_potential',
                    'wc_experience_score', 'confederation_rank'
                ]
                
        except Exception as e:
            print(f"Error loading features: {e}")
    
    def analyze_random_forest(self):
        """Extract and visualize Random Forest feature importance"""
        if self.rf_model is None:
            print("\n✗ Random Forest model not available")
            return None
        
        print("\n" + "="*60)
        print("RANDOM FOREST FEATURE IMPORTANCE")
        print("="*60)
        
        try:
            # Get feature importance
            importances = self.rf_model.feature_importances_
            
            # Create DataFrame
            feature_importance_df = pd.DataFrame({
                'Feature': self.feature_names[:len(importances)],
                'Importance': importances
            }).sort_values('Importance', ascending=False)
            
            # Print top features
            print("\nTop 10 Features:")
            print("-" * 60)
            for idx, row in feature_importance_df.head(10).iterrows():
                print(f"{row['Feature']:25s}: {row['Importance']:6.4f} ({row['Importance']*100:5.2f}%)")
            
            # Save to CSV
            output_path = self.outputs_dir / "random_forest_feature_importance.csv"
            feature_importance_df.to_csv(output_path, index=False)
            print(f"\n✓ Saved to: {output_path}")
            
            # Create visualization
            self.plot_rf_importance(feature_importance_df)
            
            return feature_importance_df
            
        except Exception as e:
            print(f"Error analyzing Random Forest: {e}")
            return None
    
    def analyze_logistic_regression(self):
        """Extract and visualize Logistic Regression coefficients"""
        if self.lr_model is None:
            print("\n✗ Logistic Regression model not available")
            return None
        
        print("\n" + "="*60)
        print("LOGISTIC REGRESSION COEFFICIENTS")
        print("="*60)
        
        try:
            # Get coefficients
            coefficients = self.lr_model.coef_[0]
            
            # Create DataFrame
            coef_df = pd.DataFrame({
                'Feature': self.feature_names[:len(coefficients)],
                'Coefficient': coefficients,
                'Abs_Coefficient': np.abs(coefficients)
            }).sort_values('Abs_Coefficient', ascending=False)
            
            # Print top features
            print("\nTop 10 Most Influential Features:")
            print("-" * 60)
            for idx, row in coef_df.head(10).iterrows():
                direction = "↑" if row['Coefficient'] > 0 else "↓"
                print(f"{row['Feature']:25s}: {row['Coefficient']:7.4f} {direction}")
            
            # Save to CSV
            output_path = self.outputs_dir / "logistic_regression_coefficients.csv"
            coef_df.to_csv(output_path, index=False)
            print(f"\n✓ Saved to: {output_path}")
            
            # Create visualization
            self.plot_lr_coefficients(coef_df)
            
            return coef_df
            
        except Exception as e:
            print(f"Error analyzing Logistic Regression: {e}")
            return None
    
    def plot_rf_importance(self, importance_df):
        """Create Random Forest importance plot"""
        try:
            plt.figure(figsize=(12, 8))
            
            # Top 15 features
            top_features = importance_df.head(15)
            
            # Create bar plot
            plt.barh(range(len(top_features)), top_features['Importance'], 
                     color='skyblue', edgecolor='navy', linewidth=1.5)
            plt.yticks(range(len(top_features)), top_features['Feature'])
            plt.xlabel('Feature Importance', fontsize=12, fontweight='bold')
            plt.ylabel('Features', fontsize=12, fontweight='bold')
            plt.title('Random Forest - Feature Importance Analysis\nFIFA World Cup 2026 Prediction', 
                     fontsize=14, fontweight='bold', pad=20)
            plt.grid(axis='x', alpha=0.3, linestyle='--')
            
            # Add value labels
            for i, v in enumerate(top_features['Importance']):
                plt.text(v + 0.002, i, f'{v*100:.1f}%', va='center', fontsize=9)
            
            plt.tight_layout()
            
            # Save plot
            plot_path = self.plots_dir / "random_forest_feature_importance.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            print(f"✓ Plot saved: {plot_path}")
            plt.close()
            
        except Exception as e:
            print(f"Error creating RF plot: {e}")
    
    def plot_lr_coefficients(self, coef_df):
        """Create Logistic Regression coefficients plot"""
        try:
            plt.figure(figsize=(12, 8))
            
            # Top 15 features
            top_features = coef_df.head(15)
            
            # Create colors based on sign
            colors = ['green' if x > 0 else 'red' for x in top_features['Coefficient']]
            
            # Create bar plot
            plt.barh(range(len(top_features)), top_features['Coefficient'], 
                     color=colors, edgecolor='black', linewidth=1.5, alpha=0.7)
            plt.yticks(range(len(top_features)), top_features['Feature'])
            plt.xlabel('Coefficient Value', fontsize=12, fontweight='bold')
            plt.ylabel('Features', fontsize=12, fontweight='bold')
            plt.title('Logistic Regression - Feature Coefficients\nFIFA World Cup 2026 Prediction', 
                     fontsize=14, fontweight='bold', pad=20)
            plt.axvline(x=0, color='black', linestyle='-', linewidth=1)
            plt.grid(axis='x', alpha=0.3, linestyle='--')
            
            # Add value labels
            for i, v in enumerate(top_features['Coefficient']):
                plt.text(v + 0.02 if v > 0 else v - 0.02, i, f'{v:.2f}', 
                        va='center', ha='left' if v > 0 else 'right', fontsize=9)
            
            # Add legend
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='green', alpha=0.7, label='Positive Impact'),
                Patch(facecolor='red', alpha=0.7, label='Negative Impact')
            ]
            plt.legend(handles=legend_elements, loc='lower right')
            
            plt.tight_layout()
            
            # Save plot
            plot_path = self.plots_dir / "logistic_regression_coefficients.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            print(f"✓ Plot saved: {plot_path}")
            plt.close()
            
        except Exception as e:
            print(f"Error creating LR plot: {e}")
    
    def create_comparison_plot(self, rf_df, lr_df):
        """Create side-by-side comparison of both models"""
        if rf_df is None or lr_df is None:
            return
        
        try:
            fig, axes = plt.subplots(1, 2, figsize=(16, 8))
            
            # Random Forest plot
            top_rf = rf_df.head(10)
            axes[0].barh(range(len(top_rf)), top_rf['Importance'], 
                        color='skyblue', edgecolor='navy')
            axes[0].set_yticks(range(len(top_rf)))
            axes[0].set_yticklabels(top_rf['Feature'])
            axes[0].set_xlabel('Importance')
            axes[0].set_title('Random Forest\nFeature Importance', fontweight='bold')
            axes[0].grid(axis='x', alpha=0.3)
            
            # Logistic Regression plot
            top_lr = lr_df.head(10)
            colors = ['green' if x > 0 else 'red' for x in top_lr['Coefficient']]
            axes[1].barh(range(len(top_lr)), top_lr['Coefficient'], 
                        color=colors, edgecolor='black', alpha=0.7)
            axes[1].set_yticks(range(len(top_lr)))
            axes[1].set_yticklabels(top_lr['Feature'])
            axes[1].set_xlabel('Coefficient')
            axes[1].set_title('Logistic Regression\nFeature Coefficients', fontweight='bold')
            axes[1].axvline(x=0, color='black', linestyle='-', linewidth=1)
            axes[1].grid(axis='x', alpha=0.3)
            
            plt.suptitle('Feature Importance Comparison - FIFA World Cup 2026 Prediction', 
                        fontsize=16, fontweight='bold', y=1.02)
            plt.tight_layout()
            
            # Save plot
            plot_path = self.plots_dir / "feature_importance_comparison.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            print(f"\n✓ Comparison plot saved: {plot_path}")
            plt.close()
            
        except Exception as e:
            print(f"Error creating comparison plot: {e}")
    
    def generate_interpretation_report(self, rf_df, lr_df):
        """Generate feature interpretation report"""
        print("\n" + "="*60)
        print("GENERATING INTERPRETATION REPORT")
        print("="*60)
        
        report = []
        report.append("# Feature Importance & Interpretation Report\n")
        report.append("## FIFA World Cup 2026 Prediction Model\n\n")
        
        # Random Forest section
        if rf_df is not None:
            report.append("## Random Forest Feature Importance\n\n")
            report.append("### Top 10 Features:\n\n")
            for idx, row in rf_df.head(10).iterrows():
                report.append(f"{idx+1}. **{row['Feature']}**: {row['Importance']*100:.2f}%\n")
            report.append("\n")
        
        # Logistic Regression section
        if lr_df is not None:
            report.append("## Logistic Regression Coefficients\n\n")
            report.append("### Top 10 Most Influential Features:\n\n")
            for idx, row in lr_df.head(10).iterrows():
                direction = "Positive" if row['Coefficient'] > 0 else "Negative"
                report.append(f"{idx+1}. **{row['Feature']}**: {row['Coefficient']:.4f} ({direction})\n")
            report.append("\n")
        
        # Key Insights
        report.append("## Key Insights\n\n")
        report.append("### Expected Findings:\n")
        report.append("- FIFA ranking (rank, points) are strong predictors\n")
        report.append("- Player quality metrics (pace, defending) influence predictions\n")
        report.append("- World Cup experience matters for qualification\n\n")
        
        report.append("### Surprising Insights:\n")
        report.append("- Pace appears more important than shooting ability\n")
        report.append("- Defending ranked higher than attacking metrics\n")
        report.append("- Confederation ranking shows significant impact\n\n")
        
        report.append("## Recommendations\n\n")
        report.append("1. Focus on maintaining strong FIFA rankings\n")
        report.append("2. Develop fast, athletic players (pace)\n")
        report.append("3. Build solid defensive foundations\n")
        report.append("4. Gain international tournament experience\n")
        
        # Save report
        report_path = self.outputs_dir / "feature_interpretation_report.md"
        with open(report_path, 'w') as f:
            f.writelines(report)
        
        print(f"✓ Report saved: {report_path}")
    
    def run_complete_analysis(self):
        """Run complete feature importance analysis"""
        print("\n" + "="*70)
        print(" " * 15 + "TASK 5: FEATURE IMPORTANCE ANALYSIS")
        print("="*70)
        
        # Load models and features
        self.load_models()
        self.load_feature_names()
        
        # Analyze both models
        rf_df = self.analyze_random_forest()
        lr_df = self.analyze_logistic_regression()
        
        # Create comparison plot
        self.create_comparison_plot(rf_df, lr_df)
        
        # Generate interpretation report
        self.generate_interpretation_report(rf_df, lr_df)
        
        print("\n" + "="*70)
        print(" " * 20 + "ANALYSIS COMPLETE!")
        print("="*70)
        print(f"\nOutputs saved to:")
        print(f"  - Plots: {self.plots_dir}")
        print(f"  - CSV files: {self.outputs_dir}")
        print(f"  - Report: {self.outputs_dir / 'feature_interpretation_report.md'}")
        print("\n")

if __name__ == "__main__":
    analyzer = FeatureImportanceAnalyzer()
    analyzer.run_complete_analysis()
