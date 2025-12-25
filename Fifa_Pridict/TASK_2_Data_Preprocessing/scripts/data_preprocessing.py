#!/usr/bin/env python3
"""
FIFA World Cup 2026 Prediction - Task 2: Model Building and Training
Data preprocessing pipeline for machine learning models

This module handles:
- Data loading and validation
- Feature engineering and selection  
- Data preprocessing (scaling, encoding)
- Train-test splitting
- Feature importance analysis
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest, f_classif, RFE
from sklearn.impute import SimpleImputer
import warnings
warnings.filterwarnings('ignore')

class FIFADataPreprocessor:
    """
    Comprehensive data preprocessing pipeline for FIFA World Cup prediction
    """
    
    def __init__(self, data_path="data/processed/top100_plus_qualified_master_dataset.csv"):
        """
        Initialize the preprocessor with data path
        
        Args:
            data_path (str): Path to the master dataset
        """
        self.data_path = data_path
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_selector = None
        self.imputer = SimpleImputer(strategy='median')
        
        # Track preprocessing steps
        self.preprocessing_steps = []
        
        print(" FIFA Data Preprocessor Initialized")
        print(f" Data source: {data_path}")
    
    def load_and_validate_data(self):
        """
        Load the master dataset and perform initial validation
        
        Returns:
            pd.DataFrame: Loaded and validated dataset
        """
        print("\n Loading and validating data...")
        
        try:
            # Load the main dataset
            df = pd.read_csv(self.data_path)
            print(f"    Loaded dataset: {df.shape[0]} teams, {df.shape[1]} features")
            
            # Display basic info
            print(f"    Date range: {df['date'].min()} to {df['date'].max()}")
            print(f"    Qualified teams: {df['qualified_2026'].sum()}")
            print(f"    Confederations: {df['confederation'].nunique()}")
            
            # Check for missing values
            missing_count = df.isnull().sum().sum()
            if missing_count > 0:
                print(f"    Missing values found: {missing_count}")
                self._show_missing_summary(df)
            else:
                print("    No missing values detected")
            
            # Validation checks
            self._validate_dataset(df)
            
            self.preprocessing_steps.append("Data loaded and validated")
            return df
            
        except FileNotFoundError:
            print(f"    Error: Dataset not found at {self.data_path}")
            return None
        except Exception as e:
            print(f"    Error loading data: {e}")
            return None
    
    def _show_missing_summary(self, df):
        """Show summary of missing values"""
        missing_data = df.isnull().sum()
        missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
        
        print("    Missing values by column:")
        for col, count in missing_data.head(10).items():
            percentage = (count / len(df)) * 100
            print(f"      • {col}: {count} ({percentage:.1f}%)")
    
    def _validate_dataset(self, df):
        """Perform validation checks on the dataset"""
        # Check required columns
        required_cols = ['team_name', 'qualified_2026', 'avg_overall', 'total.points']
        missing_required = [col for col in required_cols if col not in df.columns]
        
        if missing_required:
            print(f"    Missing required columns: {missing_required}")
        else:
            print("    All required columns present")
        
        # Check data quality
        if 'qualified_2026' in df.columns:
            target_distribution = df['qualified_2026'].value_counts()
            print(f"    Target distribution: {dict(target_distribution)}")
    
    def engineer_features(self, df):
        """
        Engineer additional features for better model performance
        
        Args:
            df (pd.DataFrame): Input dataset
            
        Returns:
            pd.DataFrame: Dataset with engineered features
        """
        print("\n Engineering additional features...")
        
        df_engineered = df.copy()
        
        # Feature 1: Team strength composite score
        if all(col in df.columns for col in ['avg_overall', 'max_overall', 'squad_size']):
            df_engineered['team_strength'] = (
                0.6 * df_engineered['avg_overall'] + 
                0.3 * df_engineered['max_overall'] + 
                0.1 * np.log1p(df_engineered['squad_size'])
            )
            print("    Created team_strength composite score")
        
        # Feature 2: Recent form indicator
        if 'points_momentum' in df.columns:
            df_engineered['form_category'] = pd.cut(
                df_engineered['points_momentum'], 
                bins=[-np.inf, -10, 10, np.inf], 
                labels=['declining', 'stable', 'improving']
            )
            print("    Created form_category feature")
        
        # Feature 3: Experience-to-quality ratio
        if all(col in df.columns for col in ['wc_experience_score', 'avg_overall']):
            df_engineered['experience_quality_ratio'] = (
                df_engineered['wc_experience_score'] / (df_engineered['avg_overall'] + 1)
            )
            print("    Created experience_quality_ratio")
        
        # Feature 4: Goal scoring efficiency
        if all(col in df.columns for col in ['total_goals', 'avg_shooting']):
            df_engineered['goal_scoring_efficiency'] = (
                df_engineered['total_goals'] / (df_engineered['avg_shooting'] + 1)
            )
            print("    Created goal_scoring_efficiency")
        
        # Feature 5: Balanced team indicator
        skill_columns = ['avg_pace', 'avg_shooting', 'avg_passing', 'avg_dribbling', 'avg_defending']
        if all(col in df.columns for col in skill_columns):
            skill_std = df_engineered[skill_columns].std(axis=1)
            df_engineered['team_balance'] = 1 / (skill_std + 1)  # Higher = more balanced
            print("    Created team_balance indicator")
        
        # Feature 6: Continental strength
        if 'confederation' in df.columns:
            confederation_strength = df_engineered.groupby('confederation')['avg_overall'].mean()
            df_engineered['continental_strength'] = df_engineered['confederation'].map(confederation_strength)
            print("    Created continental_strength feature")
        
        print(f"    Total features: {df_engineered.shape[1]} (added {df_engineered.shape[1] - df.shape[1]})")
        
        self.preprocessing_steps.append(f"Feature engineering: {df_engineered.shape[1] - df.shape[1]} new features")
        return df_engineered
    
    def prepare_features_and_target(self, df):
        """
        Prepare features and target variable for modeling
        
        Args:
            df (pd.DataFrame): Input dataset
            
        Returns:
            tuple: (X_features, y_target, feature_names)
        """
        print("\n Preparing features and target variable...")
        
        # Define target variable
        if 'qualified_2026' not in df.columns:
            raise ValueError("Target variable 'qualified_2026' not found in dataset")
        
        y = df['qualified_2026'].copy()
        print(f"    Target variable: qualified_2026")
        print(f"    Class distribution: {dict(y.value_counts())}")
        
        # Select features for modeling
        feature_columns = self._select_feature_columns(df)
        X = df[feature_columns].copy()
        
        print(f"    Selected {len(feature_columns)} features for modeling")
        
        # Handle categorical variables
        # Treat both 'object' and pandas 'category' dtypes as categorical
        categorical_columns = X.select_dtypes(include=['object', 'category']).columns.tolist()
        if categorical_columns:
            print(f"    Encoding categorical features: {categorical_columns}")
            X = self._encode_categorical_features(X, categorical_columns)
        
        # Handle missing values
        if X.isnull().sum().sum() > 0:
            print("    Imputing missing values...")
            X = pd.DataFrame(
                self.imputer.fit_transform(X),
                columns=X.columns,
                index=X.index
            )
            self.preprocessing_steps.append("Missing values imputed")
        
        print(f"    Final feature matrix: {X.shape}")
        
        self.preprocessing_steps.append(f"Features prepared: {X.shape[1]} features")
        return X, y, list(X.columns)
    
    def _select_feature_columns(self, df):
        """Select relevant columns for modeling"""
        
        # Exclude non-predictive columns
        exclude_columns = [
            'date', 'semester', 'team_name', 'acronym', 'qualified_2026',  # Target and identifiers
            'qualification_probability',  # This would be data leakage
        ]
        
        # Select numeric and categorical features
        feature_columns = [col for col in df.columns if col not in exclude_columns]
        
        # Prioritize important features
        priority_features = [
            'total.points', 'avg_overall', 'max_overall', 'squad_size',
            'wc_experience_score', 'points_momentum', 'squad_quality',
            'attack_rating', 'defense_rating', 'experience_factor',
            'confederation'
        ]
        
        # Ensure priority features come first
        ordered_features = []
        for feat in priority_features:
            if feat in feature_columns:
                ordered_features.append(feat)
        
        # Add remaining features
        for feat in feature_columns:
            if feat not in ordered_features:
                ordered_features.append(feat)
        
        return ordered_features
    
    def _encode_categorical_features(self, X, categorical_columns):
        """Encode categorical features using one-hot encoding"""
        
        for col in categorical_columns:
            if col in X.columns:
                # Use one-hot encoding for categorical variables
                dummies = pd.get_dummies(X[col], prefix=col, drop_first=True)
                X = pd.concat([X.drop(col, axis=1), dummies], axis=1)
        
        return X
    
    def scale_features(self, X_train, X_test=None):
        """
        Scale features using StandardScaler
        
        Args:
            X_train (pd.DataFrame): Training features
            X_test (pd.DataFrame, optional): Test features
            
        Returns:
            tuple: (X_train_scaled, X_test_scaled) or X_train_scaled if X_test is None
        """
        print("\n Scaling features...")
        
        # Fit scaler on training data
        X_train_scaled = pd.DataFrame(
            self.scaler.fit_transform(X_train),
            columns=X_train.columns,
            index=X_train.index
        )
        
        print(f"    Training features scaled: {X_train_scaled.shape}")
        
        if X_test is not None:
            X_test_scaled = pd.DataFrame(
                self.scaler.transform(X_test),
                columns=X_test.columns,
                index=X_test.index
            )
            print(f"    Test features scaled: {X_test_scaled.shape}")
            
            self.preprocessing_steps.append("Features scaled (train and test)")
            return X_train_scaled, X_test_scaled
        
        self.preprocessing_steps.append("Features scaled (training only)")
        return X_train_scaled
    
    def select_features(self, X_train, y_train, X_test=None, method='selectkbest', k=15):
        """
        Perform feature selection
        
        Args:
            X_train (pd.DataFrame): Training features
            y_train (pd.Series): Training target
            X_test (pd.DataFrame, optional): Test features
            method (str): Feature selection method ('selectkbest', 'rfe')
            k (int): Number of features to select
            
        Returns:
            tuple: Selected features and feature names
        """
        print(f"\n Feature selection using {method} (k={k})...")
        
        if method == 'selectkbest':
            selector = SelectKBest(score_func=f_classif, k=k)
        elif method == 'rfe':
            from sklearn.ensemble import RandomForestClassifier
            estimator = RandomForestClassifier(n_estimators=50, random_state=42)
            selector = RFE(estimator=estimator, n_features_to_select=k)
        else:
            raise ValueError(f"Unknown feature selection method: {method}")
        
        # Fit selector and transform training data
        X_train_selected = selector.fit_transform(X_train, y_train)
        selected_features = X_train.columns[selector.get_support()]
        
        print(f"    Selected {len(selected_features)} features from {X_train.shape[1]}")
        print(f"    Selected features: {list(selected_features)}")
        
        # Convert back to DataFrame
        X_train_selected = pd.DataFrame(
            X_train_selected,
            columns=selected_features,
            index=X_train.index
        )
        
        if X_test is not None:
            X_test_selected = pd.DataFrame(
                selector.transform(X_test),
                columns=selected_features,
                index=X_test.index
            )
            
            self.preprocessing_steps.append(f"Feature selection: {len(selected_features)} features selected")
            return X_train_selected, X_test_selected, list(selected_features)
        
        self.preprocessing_steps.append(f"Feature selection: {len(selected_features)} features selected")
        self.feature_selector = selector
        return X_train_selected, list(selected_features)
    
    def create_train_test_split(self, X, y, test_size=0.2, random_state=42, stratify=True):
        """
        Create train-test split with optional stratification
        
        Args:
            X (pd.DataFrame): Features
            y (pd.Series): Target variable
            test_size (float): Proportion of test set
            random_state (int): Random seed
            stratify (bool): Whether to stratify split
            
        Returns:
            tuple: (X_train, X_test, y_train, y_test)
        """
        print(f"\n Creating train-test split (test_size={test_size})...")
        
        stratify_param = y if stratify else None
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=test_size, 
            random_state=random_state, 
            stratify=stratify_param
        )
        
        print(f"    Training set: {X_train.shape[0]} samples")
        print(f"    Test set: {X_test.shape[0]} samples")
        print(f"    Train target distribution: {dict(y_train.value_counts())}")
        print(f"    Test target distribution: {dict(y_test.value_counts())}")
        
        self.preprocessing_steps.append(f"Train-test split: {X_train.shape[0]}/{X_test.shape[0]} samples")
        return X_train, X_test, y_train, y_test
    
    def get_preprocessing_summary(self):
        """
        Get summary of all preprocessing steps performed
        
        Returns:
            dict: Summary of preprocessing steps
        """
        summary = {
            'steps_performed': self.preprocessing_steps,
            'total_steps': len(self.preprocessing_steps),
            'scaler_fitted': hasattr(self.scaler, 'mean_'),
            'feature_selector_fitted': self.feature_selector is not None
        }
        
        return summary
    
    def run_complete_preprocessing(self, test_size=0.2, feature_selection_method='selectkbest', 
                                 k_features=15, random_state=42):
        """
        Run the complete preprocessing pipeline
        
        Args:
            test_size (float): Test set proportion
            feature_selection_method (str): Feature selection method
            k_features (int): Number of features to select
            random_state (int): Random seed
            
        Returns:
            dict: Complete preprocessing results
        """
        print(" Running complete preprocessing pipeline...")
        print("=" * 60)
        
        # Step 1: Load and validate data
        df = self.load_and_validate_data()
        if df is None:
            return None
        
        # Step 2: Engineer features
        df_engineered = self.engineer_features(df)
        
        # Step 3: Prepare features and target
        X, y, feature_names = self.prepare_features_and_target(df_engineered)
        
        # Step 4: Create train-test split
        X_train, X_test, y_train, y_test = self.create_train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Step 5: Scale features
        X_train_scaled, X_test_scaled = self.scale_features(X_train, X_test)
        
        # Step 6: Feature selection
        X_train_final, X_test_final, selected_features = self.select_features(
            X_train_scaled, y_train, X_test_scaled, 
            method=feature_selection_method, k=k_features
        )
        
        # Create results dictionary
        results = {
            'X_train': X_train_final,
            'X_test': X_test_final,
            'y_train': y_train,
            'y_test': y_test,
            'feature_names': selected_features,
            'original_features': feature_names,
            'preprocessing_summary': self.get_preprocessing_summary(),
            'dataset_info': {
                'total_samples': len(df),
                'total_features': len(feature_names),
                'selected_features': len(selected_features),
                'train_samples': len(X_train_final),
                'test_samples': len(X_test_final)
            }
        }
        
        print("\n" + "=" * 60)
        print(" Preprocessing pipeline completed successfully!")
        print(f" Dataset: {results['dataset_info']['total_samples']} samples")
        print(f" Features: {results['dataset_info']['selected_features']} selected from {results['dataset_info']['total_features']}")
        print(f" Split: {results['dataset_info']['train_samples']} train / {results['dataset_info']['test_samples']} test")
        print("=" * 60)
        
        return results

if __name__ == "__main__":
    # Run the preprocessing pipeline
    preprocessor = FIFADataPreprocessor()
    results = preprocessor.run_complete_preprocessing()
    
    if results:
        print("\n Preprocessing completed! Data ready for modeling.")
    else:
        print("\n Preprocessing failed. Check data availability.")