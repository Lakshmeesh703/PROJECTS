#!/usr/bin/env python3
"""
FIFA 2026 Prediction - Orchestrator CLI (Tasks 5 & 6)

Provides a command-line interface to:
- Show data sources and dataset summaries
- Refresh/Extract data via scraper (if available)
- Run preprocessing and feature engineering
- Train and evaluate models
- Generate visualizations
- Predict final tournament participants ("finalists")

Usage examples (PowerShell):
  python src/app_cli.py show-sources
  python src/app_cli.py summarize
  python src/app_cli.py list-teams --confed UEFA --top 20
  python src/app_cli.py refresh-data
  python src/app_cli.py train
  python src/app_cli.py evaluate
  python src/app_cli.py predict --top 48 --save
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
import json
import subprocess
from typing import List, Optional

import pandas as pd
import numpy as np

# Ensure project root is on sys.path so we can import local modules when run directly
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Local imports (existing modules)
from src.data_preprocessing import FIFADataPreprocessor
from src.fifa_classification_models import FIFAClassificationModels
from src.fifa_model_evaluation import FIFAModelEvaluator

DEFAULT_DATA = PROJECT_ROOT / "data" / "processed" / "top100_plus_qualified_master_dataset.csv"
MODELS_DIR = PROJECT_ROOT / "models"
PLOTS_DIR = PROJECT_ROOT / "plots"
REPORTS_DIR = PROJECT_ROOT / "reports"

def ensure_dirs():
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

def cmd_show_sources(_: argparse.Namespace) -> int:
    """Display known data sources and scraper availability."""
    sources = [
        {"name": "FIFA Rankings", "type": "CSV/API", "status": "integrated in master dataset"},
        {"name": "International Match Results", "type": "CSV", "status": "consolidated"},
        {"name": "Player Attributes (FIFA/Kaggle)", "type": "Scraped/CSV", "status": "via custom scraper"},
        {"name": "World Cup History", "type": "CSV", "status": "engineered experience features"},
        {"name": "Qualification Status", "type": "label", "status": "binary target qualified_2026"},
    ]

    scraper_path_candidates = [
        PROJECT_ROOT / "fifa_player_web_scraper.py",  # root-level script
        PROJECT_ROOT / "src" / "fifa_player_web_scraper.py",
        PROJECT_ROOT / "scripts" / "fifa_player_web_scraper.py",
    ]
    scraper_exists = any(p.exists() for p in scraper_path_candidates)

    print("Known data sources:")
    for s in sources:
        print(f" - {s['name']} [{s['type']}] -> {s['status']}")

    print(f"\nCustom scraper present: {'Yes' if scraper_exists else 'No'}")
    if scraper_exists:
        for p in scraper_path_candidates:
            if p.exists():
                print(f"  -> {p}")
    else:
        print("  (You can add the scraper at src/fifa_player_web_scraper.py)")
    return 0

def _load_master_dataset(path: Path = DEFAULT_DATA) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Master dataset not found at {path}")
    return pd.read_csv(path)

def cmd_summarize(args: argparse.Namespace) -> int:
    """Summarize the current master dataset."""
    df = _load_master_dataset(Path(args.data))
    print(f"Dataset: {args.data}")
    print(f"Rows: {len(df)}, Columns: {df.shape[1]}")
    print("Columns:", ", ".join(list(df.columns)))
    if 'date' in df.columns:
        try:
            print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        except Exception:
            pass
    if 'qualified_2026' in df.columns:
        dist = df['qualified_2026'].value_counts(dropna=False)
        print("Target distribution (qualified_2026):", dict(dist))
    if 'confederation' in df.columns:
        print("Confederations:")
        print(df['confederation'].value_counts())
    if 'team_name' in df.columns and 'total.points' in df.columns:
        print("\nTop 10 by FIFA points:")
        print(df[['team_name', 'confederation', 'total.points']].sort_values('total.points', ascending=False).head(10).to_string(index=False))
    return 0

def cmd_list_teams(args: argparse.Namespace) -> int:
    """List teams, optionally filtered and limited."""
    df = _load_master_dataset(Path(args.data))
    teams = df
    if args.confed and 'confederation' in teams.columns:
        teams = teams[teams['confederation'].str.upper() == args.confed.upper()]
    cols = ['team_name', 'confederation', 'total.points']
    cols = [c for c in cols if c in teams.columns]
    view = teams[cols] if cols else teams
    top_n = args.top if args.top else len(view)
    print(view.sort_values(cols[-1] if 'total.points' in cols else view.columns[0], ascending=False).head(top_n).to_string(index=False))
    return 0

def cmd_refresh_data(_: argparse.Namespace) -> int:
    """Run scraper/tooling to refresh raw data (if available)."""
    candidates = [
        PROJECT_ROOT / "fifa_player_web_scraper.py",
        PROJECT_ROOT / "src" / "fifa_player_web_scraper.py",
        PROJECT_ROOT / "scripts" / "fifa_player_web_scraper.py",
    ]
    scraper = next((p for p in candidates if p.exists()), None)
    if scraper is None:
        print("No scraper found. Skipping. Place your scraper at src/fifa_player_web_scraper.py")
        return 0

    print(f"Running scraper: {scraper}")
    try:
        # Delegate execution to Python; scraper should manage its own outputs
        subprocess.run([sys.executable, str(scraper)], check=True)
        print("Scraper completed. Please rerun preprocessing to incorporate updates.")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Scraper failed with exit code {e.returncode}")
        return e.returncode

def _run_preprocessing() -> dict:
    pre = FIFADataPreprocessor(data_path=str(DEFAULT_DATA))
    prep = pre.run_complete_preprocessing()
    if prep is None:
        raise RuntimeError("Preprocessing failed")
    return prep

def cmd_train(args: argparse.Namespace) -> int:
    """Train models (with tuning), save models and results."""
    ensure_dirs()
    prep = _run_preprocessing()
    clf = FIFAClassificationModels(random_state=42)
    results = clf.run_complete_classification(
        prep['X_train'], prep['X_test'], prep['y_train'], prep['y_test'], prep['feature_names'],
        tune_hyperparameters=not getattr(args, 'fast', False), perform_cv=True, save_models=True
    )
    # Save a lightweight summary
    summary = {
        'best_parameters': results.get('best_parameters', {}),
        'test_evaluation': results.get('test_evaluation', {}),
    }
    (REPORTS_DIR / 'training_summary.json').write_text(json.dumps(summary, indent=2))
    print(f"Saved training summary -> {REPORTS_DIR / 'training_summary.json'}")
    return 0

def cmd_evaluate(args: argparse.Namespace) -> int:
    """Generate evaluation plots and detailed report."""
    ensure_dirs()
    # Reuse classification flow to get predictions and metrics
    prep = _run_preprocessing()
    clf = FIFAClassificationModels(random_state=42)
    results = clf.run_complete_classification(
        prep['X_train'], prep['X_test'], prep['y_train'], prep['y_test'], prep['feature_names'],
        tune_hyperparameters=not getattr(args, 'fast', False), perform_cv=True, save_models=True
    )
    evaluator = FIFAModelEvaluator(results)
    evaluator.create_comprehensive_dashboard(prep['y_test'], save_all_plots=True)
    print("Evaluation artifacts saved to plots/ and reports/")
    return 0

def _load_best_model(models: dict) -> Optional[object]:
    # Prefer Random Forest if present
    if 'random_forest' in models:
        return models['random_forest']
    # Fall back to any
    if models:
        return list(models.values())[0]
    return None

def cmd_predict(args: argparse.Namespace) -> int:
    """Predict final tournament participants ("finalists") using best model.

    Assumptions:
    - "Finalists" here means teams predicted to qualify for the final tournament (48 teams).
    - Uses the best-performing model from the training step (Random Forest by default).
    """
    ensure_dirs()

    # Preprocess full dataset
    prep = _run_preprocessing()

    # Train (or could load from disk)
    clf = FIFAClassificationModels(random_state=42)
    results = clf.run_complete_classification(
        prep['X_train'], prep['X_test'], prep['y_train'], prep['y_test'], prep['feature_names'],
        tune_hyperparameters=not getattr(args, 'fast', False), perform_cv=False, save_models=True
    )

    model = _load_best_model(results.get('models', {}))
    if model is None:
        raise RuntimeError("No trained model available for prediction")

    # Predict probabilities on the full dataset features (need to transform X through same scaler/selection)
    # We reuse the selected features list to align columns
    selected_features: List[str] = prep['feature_names']

    # Combine train and test back to full index-aligned matrix
    X_full = pd.concat([prep['X_train'], prep['X_test']], axis=0)
    # Some models expect numpy array, but DataFrame works as long as columns align
    try:
        proba_full = model.predict_proba(X_full[selected_features])[:, 1]
    except Exception:
        # Fallback to decision_function if predict_proba unavailable
        scores = getattr(model, 'decision_function', None)
        if scores is None:
            raise
        s = scores(X_full[selected_features])
        # Min-max scale to [0,1]
        proba_full = (s - s.min()) / (s.max() - s.min() + 1e-9)

    # Attach to original dataset by index
    df_master = _load_master_dataset()
    # Align indices safely (preprocessing may shuffle); merge on team_name as stable key if available
    if 'team_name' in df_master.columns and 'team_name' in df_master.index.names:
        pass
    # Create a working frame from X_full indices
    pred_df = pd.DataFrame({
        'index': X_full.index,
        'predicted_qualification_probability': proba_full,
    })
    # Join back with team names using original row index alignment
    df_master_with_idx = df_master.copy()
    df_master_with_idx['orig_index'] = df_master_with_idx.index
    out = df_master_with_idx.merge(pred_df, left_on='orig_index', right_on='index', how='left')

    # Finalists: pick top K by probability
    top_k = int(args.top or 48)
    out_sorted = out.sort_values('predicted_qualification_probability', ascending=False).head(top_k)

    # Display summary
    display_cols = [c for c in ['team_name', 'confederation', 'total.points', 'predicted_qualification_probability'] if c in out_sorted.columns]
    print("Top predicted finalists:")
    print(out_sorted[display_cols].to_string(index=False, formatters={'predicted_qualification_probability': '{:.3f}'.format}))

    if args.save:
        save_path = PROJECT_ROOT / 'data' / 'processed' / 'finalists_predictions.csv'
        out_sorted[display_cols].to_csv(save_path, index=False)
        print(f"Saved finalists predictions -> {save_path}")
    return 0

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="FIFA 2026 Prediction - Orchestrator CLI (Tasks 5 & 6)")
    sub = p.add_subparsers(dest='command', required=True)

    sub.add_parser('show-sources', help='Display available data sources and scraper presence').set_defaults(func=cmd_show_sources)

    sp = sub.add_parser('summarize', help='Summarize the master dataset')
    sp.add_argument('--data', default=str(DEFAULT_DATA), help='Path to master dataset CSV')
    sp.set_defaults(func=cmd_summarize)

    sp = sub.add_parser('list-teams', help='List teams (optionally filtered)')
    sp.add_argument('--data', default=str(DEFAULT_DATA), help='Path to master dataset CSV')
    sp.add_argument('--confed', default=None, help='Filter by confederation (e.g., UEFA, CONMEBOL)')
    sp.add_argument('--top', type=int, default=None, help='Limit to top N by FIFA points (if available)')
    sp.set_defaults(func=cmd_list_teams)

    sub.add_parser('refresh-data', help='Run scraper to refresh raw data (if available)').set_defaults(func=cmd_refresh_data)

    sp = sub.add_parser('train', help='Run preprocessing, train models, and save')
    sp.add_argument('--fast', action='store_true', help='Skip hyperparameter tuning to train faster')
    sp.set_defaults(func=cmd_train)

    sp = sub.add_parser('evaluate', help='Run full evaluation and save plots/reports')
    sp.add_argument('--fast', action='store_true', help='Skip hyperparameter tuning for faster evaluation')
    sp.set_defaults(func=cmd_evaluate)

    sp = sub.add_parser('predict', help='Predict final tournament participants ("finalists")')
    sp.add_argument('--top', type=int, default=48, help='How many teams to output (default 48)')
    sp.add_argument('--save', action='store_true', help='Save predictions to data/processed/finalists_predictions.csv')
    sp.add_argument('--fast', action='store_true', help='Skip hyperparameter tuning for faster predictions')
    sp.set_defaults(func=cmd_predict)

    return p

def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
