"""
Random Forest Model Training for FIFA 2026 World Cup Qualification
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pickle
import os

def train_random_forest(data_path=None):
    """
    Train Random Forest model for FIFA qualification prediction
    
    Args:
        data_path: Path to the master dataset
    
    Returns:
        dict: Contains model, scaler, accuracy, and feature names
    """
    print("Training Random Forest Model\n")
    
    # Set default path if not provided
    if data_path is None:
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "TASK_2_Data_Preprocessing", "data", "processed", "top100_plus_qualified_master_dataset.csv")
    
    # Load data
    print(f"Loading data from: {data_path}")
    try:
        df = pd.read_csv(data_path)
        print(f"Loaded {len(df)} teams with {df.shape[1]} features")
    except Exception as e:
        print(f"Error loading data: {e}")
        return None
    
    # Prepare features and target
    print("\nPreparing data...")
    target_col = 'qualified_2026'
    
    # Select key features
    feature_cols = [
        'rank', 'total.points', 'previous.points',
        'wc_experience_score', 'experience_factor',
        'avg_pace', 'avg_shooting', 'avg_passing',
        'avg_dribbling', 'avg_defending', 'avg_physic',
        'wc_total_goals', 'wc_tournaments'
    ]
    
    # Filter to available columns
    available_features = [col for col in feature_cols if col in df.columns]
    print(f" Using {len(available_features)} features")
    
    # Prepare X and y
    X = df[available_features].fillna(df[available_features].median())
    y = df[target_col].fillna(0).astype(int)
    
    print(f" Features: {X.shape}")
    print(f" Target: Qualified={y.sum()}, Not Qualified={len(y)-y.sum()}")
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n Split: {len(X_train)} train / {len(X_test)} test")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest
    print("\n Training Random Forest...")
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2
    )
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    train_score = model.score(X_train_scaled, y_train)
    test_score = model.score(X_test_scaled, y_test)
    
    print(f" Training accuracy: {train_score:.4f}")
    print(f" Test accuracy: {test_score:.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': available_features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n Top 5 Most Important Features:")
    for idx, row in feature_importance.head().iterrows():
        print(f"   {row['feature']}: {row['importance']:.4f}")
    
    # Save model
    print("\n Saving model...")
    os.makedirs("models", exist_ok=True)
    model_path = "models/random_forest_fifa_2026.pkl"
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f" Saved: {model_path}")
    
    # Return results
    results = {
        'model': model,
        'scaler': scaler,
        'test_accuracy': test_score,
        'train_accuracy': train_score,
        'features': available_features,
        'feature_importance': feature_importance,
        'model_path': model_path
    }
    
    print("\n" + "=" * 60)
    print(" Random Forest training complete!")
    print(f" Test Accuracy: {test_score:.4f}")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    # Train and save model
    results = train_random_forest()
    
    if results:
        print(f"\n Model saved to: {results['model_path']}")
        print(f" Features used: {len(results['features'])}")
        print(f" Test accuracy: {results['test_accuracy']:.4f}")
