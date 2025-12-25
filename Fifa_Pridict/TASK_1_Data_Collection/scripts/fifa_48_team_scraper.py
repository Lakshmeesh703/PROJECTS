#!/usr/bin/env python3
"""
FIFA 2026 Optimized 48-Team Scraper
=====================================

Optimized version of the scraper that works only with the 48 FIFA 2026 projected teams.
Uses filtered datasets from Data_48/raw/ and integrates FIFA 26 Web Scraper for live player data.

Author: FIFA Prediction System  
Date: October 2025
"""

import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
import warnings

# Import FIFA 26 Web Scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fifa_player_web_scraper import FIFA_26_Player_Web_Scraper

warnings.filterwarnings('ignore')

class FIFA48TeamScraper:
    def __init__(self, data_48_raw=None, data_48_processed=None):
        """Initialize the optimized 48-team scraper with FIFA 26 integration"""
        if data_48_raw is None:
            data_48_raw = "d:/Fifa_Predict/Data_48/raw"
        if data_48_processed is None:
            data_48_processed = "d:/Fifa_Predict/Data_48/processed"
        
        self.data_48_raw = data_48_raw
        self.data_48_processed = data_48_processed
        
        # Create output directory
        os.makedirs(self.data_48_processed, exist_ok=True)
        
        # Initialize FIFA 26 Web Scraper
        self.fifa_26_scraper = FIFA_26_Player_Web_Scraper(
            data_raw="d:/Fifa_Predict/Data_100",
            data_processed=self.data_48_processed
        )
        
        # Optimized file paths for 48 teams only
        self.files = {
            'rankings': os.path.join(self.data_48_raw, 'fifa_rank_48_teams.csv'),
            'matches': os.path.join(self.data_48_raw, 'match_results_48_teams.csv'),
            'qualified': os.path.join(self.data_48_raw, 'fifa_2026_qualified_teams.csv'),
            'players': os.path.join(self.data_48_raw, 'fifa_26_players_48_teams.csv'),  # FIFA 26 data
            'wc_goals': os.path.join(self.data_48_raw, 'FIFA_World_Cup_Goals_48_Teams.csv')
        }
        
        print("="*70)
        print(" FIFA 2026 OPTIMIZED 48-TEAM SCRAPER")
        print("="*70)
        print(f" Source: {self.data_48_raw}")
        print(f" Output: {self.data_48_processed}")
        print(" Processing only 48 FIFA 2026 projected teams")
        print(" Player Data: FIFA 26 Web Scraper (Kaggle)")
        print()
    
    def verify_files(self):
        """Verify all required 48-team files exist"""
        print(" Verifying Optimized 48-Team Files...")
        all_exist = True
        total_size = 0
        
        for name, path in self.files.items():
            if os.path.exists(path):
                size_mb = os.path.getsize(path) / (1024 * 1024)
                total_size += size_mb
                print(f"   {name.upper()}: {size_mb:.2f} MB")
            else:
                print(f"   {name.upper()}: NOT FOUND at {path}")
                all_exist = False
        
        print(f"   Total optimized data size: {total_size:.2f} MB")
        print()
        return all_exist
    
    def load_48_teams_list(self):
        """Load the list of 48 projected teams"""
        projected_file = os.path.join(self.data_48_processed, 'projected_full_48.csv')
        
        if not os.path.exists(projected_file):
            raise FileNotFoundError(f"Projected teams file not found: {projected_file}")
        
        df_48 = pd.read_csv(projected_file)
        teams_48 = df_48['team_name'].unique().tolist()
        
        print(f" Processing {len(teams_48)} FIFA 2026 teams")
        print()
        return teams_48
    
    def process_fifa_rankings(self):
        """Process FIFA rankings for 48 teams only"""
        print(" Processing FIFA Rankings (48 teams)...")
        
        # Load the filtered rankings data
        try:
            df = pd.read_csv(self.files['rankings'])
            print(f"   Loaded: {len(df)} ranking records")
        except FileNotFoundError:
            print("    Filtered rankings file not found, using projected_full_48.csv")
            # Use the projected file as backup
            df = pd.read_csv(os.path.join(self.data_48_processed, 'projected_full_48.csv'))
            df = df.rename(columns={
                'composite_score': 'normalized_score',
                'total.points': 'total_points'
            })
        
        # Save processed rankings
        output_path = os.path.join(self.data_48_processed, 'fifa_rankings_48_teams.csv')
        df.to_csv(output_path, index=False)
        print(f"   Saved: fifa_rankings_48_teams.csv ({len(df)} teams)")
        print()
        
        return df
    
    def process_player_data(self):
        """Process player database for 48 teams only"""
        print(" Processing Player Database (48 teams)...")
        
        df_players = pd.read_csv(self.files['players'])
        print(f"   Loaded: {len(df_players)} player records for 48 teams")
        
        # Calculate squad statistics
        squad_stats = df_players.groupby('nationality_name').agg({
            'overall': ['mean', 'max', 'count'],
            'potential': 'mean',
            'age': 'mean',
            'pace': 'mean',
            'shooting': 'mean',
            'passing': 'mean',
            'dribbling': 'mean',
            'defending': 'mean',
            'physic': 'mean'
        }).round(2)
        
        # Flatten column names
        squad_stats.columns = ['_'.join(col).strip() for col in squad_stats.columns]
        squad_stats = squad_stats.rename(columns={
            'overall_mean': 'avg_overall',
            'overall_max': 'max_overall',
            'overall_count': 'squad_size',
            'potential_mean': 'avg_potential',
            'age_mean': 'avg_age',
            'pace_mean': 'avg_pace',
            'shooting_mean': 'avg_shooting',
            'passing_mean': 'avg_passing',
            'dribbling_mean': 'avg_dribbling',
            'defending_mean': 'avg_defending',
            'physic_mean': 'avg_physic'
        })
        
        squad_stats.reset_index(inplace=True)
        squad_stats.rename(columns={'nationality_name': 'team_name'}, inplace=True)
        
        # Save squad statistics
        output_squad = os.path.join(self.data_48_processed, 'squad_statistics_48_teams.csv')
        squad_stats.to_csv(output_squad, index=False)
        print(f"   Saved: squad_statistics_48_teams.csv ({len(squad_stats)} teams)")
        print()
        
        return squad_stats
    
    def process_match_results(self):
        """Process match results for 48 teams only"""
        print(" Processing Match Results (48 teams)...")
        
        df_matches = pd.read_csv(self.files['matches'])
        print(f"   Loaded: {len(df_matches)} match records involving 48 teams")
        
        # Calculate match statistics for each team
        teams_48 = self.load_48_teams_list()
        
        match_stats = []
        for team in teams_48:
            # Find home matches
            home_matches = df_matches[df_matches.iloc[:, 0] == team]  # Assume first column is home team
            # Find away matches  
            away_matches = df_matches[df_matches.iloc[:, 1] == team]  # Assume second column is away team
            
            total_matches = len(home_matches) + len(away_matches)
            
            if total_matches > 0:
                # Calculate goals (assuming goal columns exist)
                try:
                    home_goals = home_matches.iloc[:, 2].sum() if len(home_matches) > 0 else 0  # Assume 3rd column is home goals
                    away_goals = away_matches.iloc[:, 3].sum() if len(away_matches) > 0 else 0  # Assume 4th column is away goals
                    total_goals = home_goals + away_goals
                except:
                    total_goals = 0
                
                match_stats.append({
                    'team_name': team,
                    'total_matches': total_matches,
                    'total_goals': total_goals,
                    'avg_goals_per_match': round(total_goals / total_matches, 2) if total_matches > 0 else 0
                })
        
        df_match_stats = pd.DataFrame(match_stats)
        
        # Save match statistics
        output_stats = os.path.join(self.data_48_processed, 'match_statistics_48_teams.csv')
        df_match_stats.to_csv(output_stats, index=False)
        print(f"   Saved: match_statistics_48_teams.csv ({len(df_match_stats)} teams)")
        print()
        
        return df_match_stats
    
    def process_world_cup_data(self):
        """Process World Cup goals data for 48 teams only"""
        print(" Processing World Cup Data (48 teams)...")
        
        df_wc_goals = pd.read_csv(self.files['wc_goals'])
        print(f"   Loaded: {len(df_wc_goals)} World Cup goal records for 48 teams")
        
        # Calculate World Cup experience scores
        wc_stats = df_wc_goals.groupby('team_name').agg({
            'goal_id': 'count',  # Total goals scored
            'tournament_name': 'nunique'  # Number of tournaments
        }).round(2)
        
        wc_stats.columns = ['wc_total_goals', 'wc_tournaments']
        wc_stats.reset_index(inplace=True)
        
        # Calculate experience score
        wc_stats['wc_experience_score'] = (
            wc_stats['wc_total_goals'] * 0.6 + 
            wc_stats['wc_tournaments'] * 10 * 0.4
        ).round(2)
        
        # Save World Cup statistics
        output_wc = os.path.join(self.data_48_processed, 'wc_experience_48_teams.csv')
        wc_stats.to_csv(output_wc, index=False)
        print(f"   Saved: wc_experience_48_teams.csv ({len(wc_stats)} teams)")
        print()
        
        return wc_stats
    
    def create_master_dataset(self):
        """Create optimized master dataset for 48 teams"""
        print(" Creating Optimized Master Dataset (48 teams)...")
        
        # Load all processed components
        df_rankings = pd.read_csv(os.path.join(self.data_48_processed, 'fifa_rankings_48_teams.csv'))
        df_squad = pd.read_csv(os.path.join(self.data_48_processed, 'squad_statistics_48_teams.csv'))
        df_matches = pd.read_csv(os.path.join(self.data_48_processed, 'match_statistics_48_teams.csv'))
        df_wc = pd.read_csv(os.path.join(self.data_48_processed, 'wc_experience_48_teams.csv'))
        
        # Start with rankings as base
        df_master = df_rankings.copy()
        
        # Merge all components
        df_master = df_master.merge(df_squad, on='team_name', how='left')
        df_master = df_master.merge(df_matches, on='team_name', how='left')
        df_master = df_master.merge(df_wc, on='team_name', how='left')
        
        # Fill missing values
        numerical_cols = df_master.select_dtypes(include=[np.number]).columns
        df_master[numerical_cols] = df_master[numerical_cols].fillna(0)
        
        # Calculate derived features
        print("   Engineering features...")
        
        # Squad quality
        if all(col in df_master.columns for col in ['avg_overall', 'max_overall', 'squad_size']):
            df_master['squad_quality'] = (
                (df_master['avg_overall'] + df_master['max_overall']) / 2
            ).round(2)
        
        # Attack rating
        if all(col in df_master.columns for col in ['avg_shooting', 'avg_pace', 'avg_dribbling']):
            df_master['attack_rating'] = (
                (df_master['avg_shooting'] + df_master['avg_pace'] + df_master['avg_dribbling']) / 3
            ).round(2)
        
        # Defense rating
        if all(col in df_master.columns for col in ['avg_defending', 'avg_physic']):
            df_master['defense_rating'] = (
                (df_master['avg_defending'] + df_master['avg_physic']) / 2
            ).round(2)
        
        # Goal efficiency
        if 'total_goals' in df_master.columns and 'total_matches' in df_master.columns:
            df_master['goal_efficiency'] = (
                df_master['total_goals'] / df_master['total_matches'].replace(0, 1)
            ).round(2)
        
        # Experience factor
        if all(col in df_master.columns for col in ['wc_tournaments', 'wc_experience_score']):
            df_master['experience_factor'] = (
                df_master['wc_tournaments'] * 0.4 + 
                df_master['wc_experience_score'] * 0.6
            ).round(2)
        
        # Qualification probability (based on composite score)
        if 'composite_score' in df_master.columns:
            df_master['qualification_probability'] = df_master['composite_score']
        elif 'rank' in df_master.columns:
            df_master['qualification_probability'] = (
                (49 - df_master['rank']) / 48
            ).clip(0, 1).round(3)
        
        # Save master dataset
        output_path = os.path.join(self.data_48_processed, 'master_dataset_48_teams.csv')
        df_master.to_csv(output_path, index=False)
        print(f"   Saved: master_dataset_48_teams.csv")
        print(f"   Shape: {df_master.shape[0]} teams × {df_master.shape[1]} features")
        print()
        
        return df_master
    
    def run_optimized_processing(self):
        """Run the complete optimized processing pipeline"""
        try:
            print(" Starting FIFA 2026 Optimized Processing...")
            print()
            
            # Verify files
            if not self.verify_files():
                raise FileNotFoundError("Required 48-team data files are missing")
            
            # Process each component
            df_rankings = self.process_fifa_rankings()
            df_squad = self.process_player_data()
            df_matches = self.process_match_results()
            df_wc = self.process_world_cup_data()
            
            # Create master dataset
            df_master = self.create_master_dataset()
            
            print("="*70)
            print(" FIFA 2026 OPTIMIZED PROCESSING COMPLETED!")
            print("="*70)
            print(f" Processed: 48 FIFA 2026 projected teams")
            print(f" Master Dataset: {df_master.shape[1]} engineered features")
            print(f" Output: {self.data_48_processed}")
            print()
            print(" Ready for optimized FIFA 2026 ML training!")
            
        except Exception as e:
            print(f" Error during optimized processing: {str(e)}")
            raise

if __name__ == "__main__":
    scraper = FIFA48TeamScraper()
    scraper.run_optimized_processing()