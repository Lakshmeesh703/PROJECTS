"""
FIFA 2026 Prediction - Data_100 Scraper & Cleaner

Scrapes and cleans data from Data_100 Kaggle datasets for ML training
Now integrates with FIFA 26 Web Scraper for live player data

Author: FIFA Prediction Team
Date: October 21, 2025
"""

import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime
import warnings

# Import FIFA 26 Web Scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fifa_player_web_scraper import FIFA_26_Player_Web_Scraper

warnings.filterwarnings('ignore')

class Data100Scraper:
    """Scraper for Data_100 Kaggle datasets"""
    
    def __init__(self, data_raw='../Data_100', data_processed='../data/processed'):
        self.data_raw = data_raw
        self.data_processed = data_processed
        
        # Create output directory
        os.makedirs(self.data_processed, exist_ok=True)
        
        # Initialize FIFA 26 Web Scraper
        self.fifa_26_scraper = FIFA_26_Player_Web_Scraper(
            data_raw=self.data_raw,
            data_processed=self.data_processed
        )
        
        # File paths - using web scraper for player data
        self.files = {
            'rankings': os.path.join(self.data_raw, 'fifa_rank Top 210.csv'),
            'matches': os.path.join(self.data_raw, 'International_football_result.csv'),
            'qualified': os.path.join(self.data_raw, 'FIFA_2026_Qualified_Teams.csv'),
            'players': os.path.join(self.data_raw, 'FIFA_Player_Database_Web.csv'),  # Now uses web data
            'wc_goals': os.path.join(self.data_raw, 'FIFA World Cup All Goals 1930-2022.csv')
        }
        
        print("="*70)
        print(" FIFA DATA_100 SCRAPER INITIALIZED")
        print("="*70)
        print(f" Source: {self.data_raw}")
        print(f" Output: {self.data_processed}")
        print(" Player Data: FIFA 26 Web Scraper (Kaggle)")
        print()
        
    def verify_files(self):
        """Verify all required files exist and ensure FIFA 26 data is ready"""
        print(" Verifying Data_100 Files...")
        
        # First ensure FIFA 26 player data is available
        print(" Checking FIFA 26 Web Data...")
        fifa_26_ready = self.fifa_26_scraper.show_running_data_status()
        
        if not fifa_26_ready:
            print(" FIFA 26 data not available, attempting to process...")
            fifa_result = self.fifa_26_scraper.integrate_with_existing_scraper()
            if fifa_result is None:
                print(" Failed to get FIFA 26 data. Please download manually:")
                print(" https://www.kaggle.com/datasets/rovnez/fc-26-fifa-26-player-data")
                return False
        
        print("\n Verifying other Data_100 files...")
        all_exist = True
        
        for name, path in self.files.items():
            if os.path.exists(path):
                size_mb = os.path.getsize(path) / (1024 * 1024)
                print(f"   {name.upper()}: {size_mb:.2f} MB")
            else:
                print(f"   {name.upper()}: NOT FOUND at {path}")
                all_exist = False
        
        print()
        return all_exist
    
    def scrape_rankings(self):
        """Scrape and clean FIFA rankings"""
        print(" Scraping FIFA Rankings...")
        
        # Try different encodings
        for encoding in ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']:
            try:
                df = pd.read_csv(self.files['rankings'], encoding=encoding)
                print(f"  Raw: {len(df)} teams (encoding: {encoding})")
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError("Could not decode rankings file with any common encoding")
        
        # Filter Semester 2 (most recent)
        df_clean = df[df['semester'] == 2].copy()
        
        # Clean data
        df_clean['total.points'].fillna(0, inplace=True)
        df_clean['previous.points'].fillna(0, inplace=True)
        df_clean['diff.points'].fillna(0, inplace=True)
        df_clean['team'] = df_clean['team'].str.strip()
        df_clean['acronym'] = df_clean['acronym'].str.strip()
        
        # Remove duplicates
        df_clean = df_clean.drop_duplicates(subset=['team'], keep='first')
        df_clean = df_clean.sort_values('rank').reset_index(drop=True)
        
        print(f"  Cleaned: {len(df_clean)} teams (Semester 2)")
        
        # Save full rankings
        output_path = os.path.join(self.data_processed, 'fifa_rankings_clean.csv')
        df_clean.to_csv(output_path, index=False)
        print(f"   Saved: fifa_rankings_clean.csv")
        
        # Create Top 100
        df_top100 = df_clean.head(100).copy()
        output_top100 = os.path.join(self.data_processed, 'fifa_top100.csv')
        df_top100.to_csv(output_top100, index=False)
        print(f"   Saved: fifa_top100.csv (100 teams)")
        
        print()
        return df_clean, df_top100
    
    def scrape_matches(self):
        """Scrape and clean match results"""
        print(" Scraping Match Results...")
        
        # Try different encodings
        for encoding in ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']:
            try:
                df = pd.read_csv(self.files['matches'], encoding=encoding)
                print(f"  Raw: {len(df):,} matches (encoding: {encoding})")
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError("Could not decode matches file with any common encoding")
        
        # Convert date
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
        df = df.dropna(subset=['date'])
        
        # Filter recent matches (2015+)
        df_clean = df[df['date'] >= '2015-01-01'].copy()
        
        # Clean team names
        df_clean['home_team'] = df_clean['home_team'].str.strip()
        df_clean['away_team'] = df_clean['away_team'].str.strip()
        df_clean['team'] = df_clean['team'].str.strip()
        
        # Convert booleans
        df_clean['own_goal'] = df_clean['own_goal'].astype(str).str.upper() == 'TRUE'
        df_clean['penalty'] = df_clean['penalty'].astype(str).str.upper() == 'TRUE'
        
        # Remove duplicates
        df_clean = df_clean.drop_duplicates()
        
        print(f"  Cleaned: {len(df_clean):,} matches (2015-2025)")
        
        # Save
        output_path = os.path.join(self.data_processed, 'match_results_clean.csv')
        df_clean.to_csv(output_path, index=False)
        print(f"   Saved: match_results_clean.csv")
        
        # Aggregate statistics
        df_stats = self._aggregate_match_stats(df_clean)
        output_stats = os.path.join(self.data_processed, 'match_statistics.csv')
        df_stats.to_csv(output_stats, index=False)
        print(f"   Saved: match_statistics.csv ({len(df_stats)} teams)")
        
        print()
        return df_clean, df_stats
    
    def _aggregate_match_stats(self, df):
        """Aggregate match statistics by team"""
        total_goals = df.groupby('team').size().rename('total_goals')
        penalties = df[df['penalty'] == True].groupby('team').size().rename('penalty_goals')
        own_goals = df[df['own_goal'] == True].groupby('team').size().rename('own_goals')
        
        df_stats = pd.DataFrame({
            'team_name': total_goals.index,
            'total_goals': total_goals.values,
            'penalty_goals': penalties.reindex(total_goals.index, fill_value=0).values,
            'own_goals': own_goals.reindex(total_goals.index, fill_value=0).values
        })
        
        df_stats['clean_goals'] = df_stats['total_goals'] - df_stats['penalty_goals'] - df_stats['own_goals']
        
        return df_stats
    
    def scrape_qualified_teams(self):
        """Scrape qualified teams for 2026"""
        print(" Scraping 2026 Qualified Teams...")
        # Try different encodings (some CSVs include special chars like Côte d'Ivoire)
        for encoding in ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']:
            try:
                df = pd.read_csv(self.files['qualified'], encoding=encoding)
                print(f"  Raw: {len(df)} teams (encoding: {encoding})")
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError("Could not decode qualified teams file with any common encoding")

        # Clean
        df_clean = df.copy()
        for col in ['team', 'confederation', 'status']:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip()

        # Standardize team names to match FIFA ranking naming
        # This ensures merges with rankings succeed (e.g., South Korea -> Korea Republic)
        name_map = {
            'South Korea': 'Korea Republic',
            'North Korea': 'Korea DPR',
            'Ivory Coast': "Côte d'Ivoire",
            'Cape Verde': 'Cabo Verde',
            'IR Iran': 'IR Iran',  # keep as-is if already normalized
            'Iran': 'IR Iran',
            'UAE': 'United Arab Emirates',
            'United States': 'USA',  # rankings use USA
            'USA': 'USA',
            'Congo DR': 'Congo DR',
            'DR Congo': 'Congo DR',
        }
        df_clean['team_norm'] = df_clean['team'].replace(name_map)

        # Prefer normalized names for downstream joins
        df_clean['team'] = df_clean['team_norm']
        df_clean = df_clean.drop(columns=['team_norm'])

        # Remove duplicates after normalization
        df_clean = df_clean.drop_duplicates(subset=['team'], keep='first')

        print(f"  Cleaned: {len(df_clean)} qualified teams")
        print(f"  Confederations: {df_clean['confederation'].value_counts().to_dict()}")

        # Save
        output_path = os.path.join(self.data_processed, 'qualified_teams_clean.csv')
        df_clean.to_csv(output_path, index=False)
        print(f"   Saved: qualified_teams_clean.csv")

        print()
        return df_clean
    
    def scrape_players(self):
        """Scrape player database"""
        print(" Scraping Player Database...")
        
        # Try different encodings
        for encoding in ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']:
            try:
                df = pd.read_csv(self.files['players'], encoding=encoding)
                print(f"  Raw: {len(df):,} players (encoding: {encoding})")
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError("Could not decode players file with any common encoding")
        
        # Select relevant columns
        player_cols = [
            'nationality_name', 'overall', 'potential', 'age', 'height_cm', 'weight_kg',
            'preferred_foot', 'weak_foot', 'skill_moves', 'international_reputation',
            'pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic'
        ]
        available_cols = [col for col in player_cols if col in df.columns]
        df_clean = df[available_cols].copy()
        
        # Clean
        df_clean['nationality_name'] = df_clean['nationality_name'].str.strip()
        df_clean = df_clean.dropna(subset=['nationality_name'])
        
        # Fill missing numeric values
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            df_clean[col].fillna(df_clean[col].median(), inplace=True)
        
        # Remove duplicates
        df_clean = df_clean.drop_duplicates()
        
        print(f"  Cleaned: {len(df_clean):,} players")
        print(f"  Nationalities: {df_clean['nationality_name'].nunique()}")
        
        # Aggregate by nationality
        df_squad = self._aggregate_squad_stats(df_clean)
        output_squad = os.path.join(self.data_processed, 'squad_statistics.csv')
        df_squad.to_csv(output_squad, index=False)
        print(f"   Saved: squad_statistics.csv ({len(df_squad)} teams)")
        
        print()
        return df_clean, df_squad
    
    def _aggregate_squad_stats(self, df):
        """Aggregate squad statistics by nationality"""
        df_stats = df.groupby('nationality_name').agg({
            'overall': ['mean', 'max', 'count'],
            'potential': 'mean',
            'age': 'mean',
            'pace': 'mean',
            'shooting': 'mean',
            'passing': 'mean',
            'dribbling': 'mean',
            'defending': 'mean',
            'physic': 'mean'
        }).reset_index()
        
        # Flatten columns
        df_stats.columns = ['team_name', 'avg_overall', 'max_overall', 'squad_size',
                           'avg_potential', 'avg_age', 'avg_pace', 'avg_shooting',
                           'avg_passing', 'avg_dribbling', 'avg_defending', 'avg_physic']
        
        # Round
        numeric_cols = df_stats.select_dtypes(include=[np.number]).columns
        df_stats[numeric_cols] = df_stats[numeric_cols].round(2)
        
        return df_stats
    
    def scrape_wc_goals(self):
        """Scrape World Cup goals history"""
        print(" Scraping World Cup Goals (1930-2022)...")
        
        # Try different encodings
        for encoding in ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']:
            try:
                df = pd.read_csv(self.files['wc_goals'], encoding=encoding)
                print(f"  Raw: {len(df):,} goals (encoding: {encoding})")
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError("Could not decode WC goals file with any common encoding")
        
        # Clean
        df_clean = df.copy()
        df_clean['team_name'] = df_clean['team_name'].str.strip()
        df_clean['match_date'] = pd.to_datetime(df_clean['match_date'], errors='coerce')
        df_clean = df_clean.dropna(subset=['match_date'])
        
        # Convert booleans
        df_clean['own_goal'] = df_clean['own_goal'].astype(int)
        df_clean['penalty'] = df_clean['penalty'].astype(int)
        
        # Remove duplicates
        df_clean = df_clean.drop_duplicates()
        
        print(f"  Cleaned: {len(df_clean):,} goals")
        
        # Calculate WC experience scores
        df_wc_exp = self._calculate_wc_experience(df_clean)
        output_wc = os.path.join(self.data_processed, 'wc_experience_scores.csv')
        df_wc_exp.to_csv(output_wc, index=False)
        print(f"   Saved: wc_experience_scores.csv ({len(df_wc_exp)} teams)")
        
        print()
        return df_clean, df_wc_exp
    
    def _calculate_wc_experience(self, df):
        """Calculate World Cup experience scores"""
        df_exp = df.groupby('team_name').agg({
            'goal_id': 'count',
            'penalty': 'sum',
            'own_goal': 'sum',
            'tournament_id': 'nunique'
        }).reset_index()
        
        df_exp.columns = ['team_name', 'wc_total_goals', 'wc_penalties', 'wc_own_goals', 'wc_tournaments']
        
        # Calculate experience score (weighted)
        df_exp['wc_experience_score'] = (
            (df_exp['wc_tournaments'] * 10) +
            (df_exp['wc_total_goals'] * 2) +
            (df_exp['wc_penalties'] * 1)
        ).round(2)
        
        return df_exp
    
    def create_master_dataset(self, df_rankings, df_match_stats, df_qualified, df_squad, df_wc_exp):
        """Create master Top 100 dataset with all features"""
        print(" Creating Master Top 100 Dataset...")
        
        # Start with Top 100 rankings
        df_top100 = df_rankings.head(100).copy()
        df_master = df_top100.rename(columns={'team': 'team_name'})
        
        print(f"  Base: {len(df_master)} teams")
        
        # Add qualification status
        df_qualified['qualified_2026'] = 1
        df_master = df_master.merge(
            df_qualified[['team', 'confederation', 'qualified_2026']],
            left_on='team_name',
            right_on='team',
            how='left'
        )
        df_master['qualified_2026'] = df_master['qualified_2026'].fillna(0).astype(int)
        if 'team' in df_master.columns:
            df_master = df_master.drop(columns=['team'])
        
        # Fill missing confederations based on team knowledge
        confederation_map = {
            'France': 'UEFA', 'Spain': 'UEFA', 'Portugal': 'UEFA', 'Netherlands': 'UEFA',
            'Belgium': 'UEFA', 'Italy': 'UEFA', 'Germany': 'UEFA', 'Croatia': 'UEFA',
            'Switzerland': 'UEFA', 'Denmark': 'UEFA', 'Austria': 'UEFA', 'Turkey': 'UEFA',
            'Ukraine': 'UEFA', 'Poland': 'UEFA', 'Greece': 'UEFA', 'Czech Republic': 'UEFA',
            'Hungary': 'UEFA', 'Norway': 'UEFA', 'Serbia': 'UEFA', 'Slovakia': 'UEFA',
            'Romania': 'UEFA', 'Sweden': 'UEFA', 'Russia': 'UEFA', 'Slovenia': 'UEFA',
            'Finland': 'UEFA', 'Wales': 'UEFA', 'Scotland': 'UEFA', 'Ireland': 'UEFA',
            'Northern Ireland': 'UEFA', 'Israel': 'UEFA', 'Iceland': 'UEFA', 'Georgia': 'UEFA',
            'Luxembourg': 'UEFA', 'Estonia': 'UEFA', 'Latvia': 'UEFA', 'Lithuania': 'UEFA',
            'Moldova': 'UEFA', 'Albania': 'UEFA', 'Montenegro': 'UEFA', 'North Macedonia': 'UEFA',
            'Bosnia and Herzegovina': 'UEFA', 'Bulgaria': 'UEFA', 'Kazakhstan': 'UEFA',
            'Azerbaijan': 'UEFA', 'Belarus': 'UEFA', 'Armenia': 'UEFA', 'Cyprus': 'UEFA',
            'Faroe Islands': 'UEFA', 'Malta': 'UEFA', 'Andorra': 'UEFA', 'San Marino': 'UEFA',
            'Liechtenstein': 'UEFA', 'Gibraltar': 'UEFA', 'Kosovo': 'UEFA',
            'China': 'AFC', 'Thailand': 'AFC', 'India': 'AFC', 'Indonesia': 'AFC',
            'Philippines': 'AFC', 'Malaysia': 'AFC', 'Singapore': 'AFC', 'Vietnam': 'AFC',
            'Myanmar': 'AFC', 'Cambodia': 'AFC', 'Laos': 'AFC', 'Bangladesh': 'AFC',
            'Sri Lanka': 'AFC', 'Maldives': 'AFC', 'Nepal': 'AFC', 'Bhutan': 'AFC',
            'Chinese Taipei': 'AFC', 'Hong Kong': 'AFC', 'Macau': 'AFC', 'Mongolia': 'AFC',
            'Lebanon': 'AFC', 'Palestine': 'AFC', 'Syria': 'AFC', 'Yemen': 'AFC',
            'Oman': 'AFC', 'Bahrain': 'AFC', 'Kuwait': 'AFC', 'Iraq': 'AFC',
            'South Sudan': 'CAF', 'Madagascar': 'CAF', 'Mozambique': 'CAF', 'Zimbabwe': 'CAF',
            'Zambia': 'CAF', 'Botswana': 'CAF', 'Namibia': 'CAF', 'Malawi': 'CAF',
            'Eswatini': 'CAF', 'Lesotho': 'CAF', 'Angola': 'CAF', 'Central African Republic': 'CAF',
            'Chad': 'CAF', 'Congo': 'CAF', 'Equatorial Guinea': 'CAF', 'Gabon': 'CAF',
            'Sao Tome and Principe': 'CAF', 'Cameroon': 'CAF', 'Nigeria': 'CAF',
            'Benin': 'CAF', 'Togo': 'CAF', 'Ghana': 'CAF', 'Burkina Faso': 'CAF',
            'Mali': 'CAF', 'Niger': 'CAF', 'Guinea': 'CAF', 'Guinea-Bissau': 'CAF',
            'Sierra Leone': 'CAF', 'Liberia': 'CAF', 'Gambia': 'CAF', 'Mauritania': 'CAF',
            'Sudan': 'CAF', 'Eritrea': 'CAF', 'Ethiopia': 'CAF', 'Djibouti': 'CAF',
            'Somalia': 'CAF', 'Kenya': 'CAF', 'Uganda': 'CAF', 'Tanzania': 'CAF',
            'Rwanda': 'CAF', 'Burundi': 'CAF', 'Comoros': 'CAF', 'Mauritius': 'CAF',
            'Seychelles': 'CAF', 'Libya': 'CAF', 'DR Congo': 'CAF', 'Congo DR': 'CAF',
            'Jamaica': 'CONCACAF', 'Trinidad and Tobago': 'CONCACAF', 'Haiti': 'CONCACAF',
            'Guatemala': 'CONCACAF', 'Honduras': 'CONCACAF', 'El Salvador': 'CONCACAF',
            'Nicaragua': 'CONCACAF', 'Costa Rica': 'CONCACAF', 'Panama': 'CONCACAF',
            'Cuba': 'CONCACAF', 'Dominican Republic': 'CONCACAF', 'Puerto Rico': 'CONCACAF',
            'Barbados': 'CONCACAF', 'Grenada': 'CONCACAF', 'Saint Vincent and the Grenadines': 'CONCACAF',
            'Saint Lucia': 'CONCACAF', 'Dominica': 'CONCACAF', 'Antigua and Barbuda': 'CONCACAF',
            'Saint Kitts and Nevis': 'CONCACAF', 'Bermuda': 'CONCACAF', 'Belize': 'CONCACAF',
            'Guyana': 'CONCACAF', 'Suriname': 'CONCACAF', 'French Guiana': 'CONCACAF',
            'Peru': 'CONMEBOL', 'Chile': 'CONMEBOL', 'Bolivia': 'CONMEBOL', 'Venezuela': 'CONMEBOL',
            'Fiji': 'OFC', 'Papua New Guinea': 'OFC', 'Solomon Islands': 'OFC',
            'Vanuatu': 'OFC', 'Samoa': 'OFC', 'Tonga': 'OFC', 'Cook Islands': 'OFC',
            'Tahiti': 'OFC', 'American Samoa': 'OFC'
        }
        
        # Apply confederation mapping for missing values
        df_master['confederation'] = df_master.apply(
            lambda row: confederation_map.get(row['team_name'], row['confederation']) 
            if pd.isna(row['confederation']) or row['confederation'] == '' 
            else row['confederation'], 
            axis=1
        )
        
        print(f"  + Qualification: {df_master['qualified_2026'].sum()} qualified")
        
        # Add match statistics
        df_master = df_master.merge(df_match_stats, on='team_name', how='left')
        match_cols = ['total_goals', 'penalty_goals', 'own_goals', 'clean_goals']
        df_master[match_cols] = df_master[match_cols].fillna(0)
        print(f"  + Match stats")
        
        # Add squad statistics
        df_master = df_master.merge(df_squad, on='team_name', how='left')
        squad_cols = ['avg_overall', 'max_overall', 'squad_size', 'avg_potential', 'avg_age',
                     'avg_pace', 'avg_shooting', 'avg_passing', 'avg_dribbling', 'avg_defending', 'avg_physic']
        for col in squad_cols:
            if col in df_master.columns:
                df_master[col] = df_master[col].fillna(df_master[col].median())
        print(f"  + Squad stats")
        
        # Add WC experience
        df_master = df_master.merge(
            df_wc_exp[['team_name', 'wc_total_goals', 'wc_tournaments', 'wc_experience_score']],
            on='team_name',
            how='left'
        )
        wc_cols = ['wc_total_goals', 'wc_tournaments', 'wc_experience_score']
        df_master[wc_cols] = df_master[wc_cols].fillna(0)
        print(f"  + WC experience")
        
        # Engineer additional features
        df_master = self._engineer_features(df_master)
        print(f"  + Engineered features")
        
        print(f"  Final: {df_master.shape[0]} teams × {df_master.shape[1]} features")
        
        # Save
        output_path = os.path.join(self.data_processed, 'top100_master_dataset.csv')
        df_master.to_csv(output_path, index=False)
        print(f"   Saved: top100_master_dataset.csv")
        
        print()
        return df_master
    
    def _engineer_features(self, df):
        """Engineer additional ML features"""
        # Points momentum
        df['points_momentum'] = df['diff.points']
        
        # Squad quality score
        if 'avg_overall' in df.columns:
            df['squad_quality'] = ((df['avg_overall'] * 0.6) + (df['avg_potential'] * 0.4)).round(2)
        else:
            df['squad_quality'] = 0
        
        # Attack rating
        if all(col in df.columns for col in ['avg_shooting', 'avg_pace', 'avg_dribbling']):
            df['attack_rating'] = ((df['avg_shooting'] + df['avg_pace'] + df['avg_dribbling']) / 3).round(2)
        else:
            df['attack_rating'] = 0
        
        # Defense rating
        if all(col in df.columns for col in ['avg_defending', 'avg_physic']):
            df['defense_rating'] = ((df['avg_defending'] + df['avg_physic']) / 2).round(2)
        else:
            df['defense_rating'] = 0
        
        # Goal efficiency
        if 'total_goals' in df.columns:
            df['goal_efficiency'] = (df['total_goals'] / 100).round(2)
        else:
            df['goal_efficiency'] = 0
        
        # Experience factor
        max_tournaments = df['wc_tournaments'].max()
        if max_tournaments > 0:
            df['experience_factor'] = (df['wc_tournaments'] / max_tournaments).round(2)
        else:
            df['experience_factor'] = 0
        
        # Qualification probability
        df['qualification_probability'] = df.apply(
            lambda row: 1.0 if row['qualified_2026'] == 1 else max(0.1, (50 - row['rank']) / 50) if row['rank'] <= 50 else 0.05,
            axis=1
        ).round(2)
        
        return df
    
    def compute_composite_score(self, df_master):
        """Compute composite score for remaining team projections"""
        df = df_master.copy()
        
        # Normalize features (0-1 scale)
        df['norm_points'] = (df['total.points'] - df['total.points'].min()) / (df['total.points'].max() - df['total.points'].min())
        df['norm_inverse_rank'] = (101 - df['rank']) / 100  # Higher rank = lower number = better
        df['norm_squad_quality'] = df['squad_quality'] / 100  # Assuming 0-100 scale
        df['norm_attack_rating'] = df['attack_rating'] / 100
        df['norm_defense_rating'] = df['defense_rating'] / 100
        df['norm_goal_efficiency'] = df['goal_efficiency'] / df['goal_efficiency'].max() if df['goal_efficiency'].max() > 0 else 0
        df['norm_experience'] = df['experience_factor']  # Already 0-1
        df['norm_momentum'] = np.maximum(0, df['points_momentum']) / 50  # Clip negatives, scale positives
        
        # Composite score with weights
        weights = {
            'points': 0.30,
            'rank': 0.15,
            'squad': 0.20,
            'attack': 0.10,
            'defense': 0.10,
            'efficiency': 0.05,
            'experience': 0.05,
            'momentum': 0.05
        }
        
        df['composite_score'] = (
            weights['points'] * df['norm_points'] +
            weights['rank'] * df['norm_inverse_rank'] +
            weights['squad'] * df['norm_squad_quality'] +
            weights['attack'] * df['norm_attack_rating'] +
            weights['defense'] * df['norm_defense_rating'] +
            weights['efficiency'] * df['norm_goal_efficiency'] +
            weights['experience'] * df['norm_experience'] +
            weights['momentum'] * df['norm_momentum']
        ).round(4)
        
        return df
    
    def project_remaining_20_teams(self, df_master):
        """Project remaining 20 teams for FIFA 2026 (48 total)"""
        print(" Projecting Remaining 20 Teams for FIFA 2026...")
        
        # Add composite scores
        df = self.compute_composite_score(df_master)
        
        # FIFA 2026 allocation (48 teams total)
        confed_quotas = {
            'UEFA': 16,
            'CONCACAF': 6, 
            'AFC': 8,
            'CAF': 9,
            'CONMEBOL': 6,
            'OFC': 1
        }
        
        # Count current qualified by confederation
        qualified_teams = df[df['qualified_2026'] == 1]
        current_by_confed = qualified_teams.groupby('confederation').size().to_dict()
        
        print(f"  Current qualified: {len(qualified_teams)} teams")
        for confed, count in current_by_confed.items():
            quota = confed_quotas.get(confed, 0)
            remaining = max(0, quota - count)
            print(f"    {confed}: {count}/{quota} (need {remaining} more)")
        
        # Project direct qualifiers
        direct_projections = []
        playoff_candidates = []
        
        # Non-qualified teams for projections
        non_qualified = df[df['qualified_2026'] == 0].copy()
        
        # Direct slots (18 teams: UEFA 15 + CONCACAF 3)
        for confed in ['UEFA', 'CONCACAF']:
            current_count = current_by_confed.get(confed, 0)
            quota = confed_quotas[confed]
            needed = quota - current_count
            
            if needed > 0:
                confed_teams = non_qualified[non_qualified['confederation'] == confed]
                if len(confed_teams) > 0:
                    confed_teams = confed_teams.nlargest(needed, 'composite_score')
                    direct_projections.append(confed_teams)
        
        # Playoff candidates (from confederations that can enter playoffs)
        playoff_eligible = ['AFC', 'CAF', 'CONMEBOL', 'OFC', 'CONCACAF']
        for confed in playoff_eligible:
            confed_teams = non_qualified[non_qualified['confederation'] == confed]
            if len(confed_teams) > 0:
                # Take top 2 candidates per confederation for playoff pool
                top_candidates = confed_teams.nlargest(2, 'composite_score')
                playoff_candidates.append(top_candidates)
        
        # Combine direct projections
        if direct_projections:
            df_direct = pd.concat(direct_projections, ignore_index=True)
        else:
            df_direct = pd.DataFrame()
        
        # Combine playoff candidates and select top 2
        if playoff_candidates:
            df_playoff_pool = pd.concat(playoff_candidates, ignore_index=True)
            df_playoff_winners = df_playoff_pool.nlargest(2, 'composite_score')
        else:
            df_playoff_pool = pd.DataFrame()
            df_playoff_winners = pd.DataFrame()
        
        print(f"  Direct projections: {len(df_direct)} teams")
        print(f"  Playoff winners: {len(df_playoff_winners)} teams")
        
        # Save projection files
        self._save_projection_outputs(df_direct, df_playoff_pool, df_playoff_winners, qualified_teams)
        
        return df_direct, df_playoff_winners
    
    def _save_projection_outputs(self, df_direct, df_playoff_pool, df_playoff_winners, qualified_teams):
        """Save projection output files"""
        
        # Direct qualifiers
        if len(df_direct) > 0:
            direct_output = df_direct[['team_name', 'confederation', 'composite_score', 'rank', 'total.points']].copy()
            direct_output['status'] = 'Projected (Direct)'
            direct_path = os.path.join(self.data_processed, 'projected_direct_18.csv')
            direct_output.to_csv(direct_path, index=False)
            print(f"   Saved: projected_direct_18.csv ({len(direct_output)} teams)")
        
        # Playoff candidates
        if len(df_playoff_pool) > 0:
            playoff_output = df_playoff_pool[['team_name', 'confederation', 'composite_score', 'rank', 'total.points']].copy()
            playoff_path = os.path.join(self.data_processed, 'projected_playoff_candidates.csv')
            playoff_output.to_csv(playoff_path, index=False)
            print(f"   Saved: projected_playoff_candidates.csv ({len(playoff_output)} teams)")
        
        # Playoff winners
        if len(df_playoff_winners) > 0:
            winners_output = df_playoff_winners[['team_name', 'confederation', 'composite_score', 'rank', 'total.points']].copy()
            winners_output['status'] = 'Projected (Playoff)'
            winners_path = os.path.join(self.data_processed, 'projected_playoff_winners.csv')
            winners_output.to_csv(winners_path, index=False)
            print(f"   Saved: projected_playoff_winners.csv ({len(winners_output)} teams)")
        
        # Full 48-team dataset
        full_48_list = []
        
        # Add qualified teams
        qualified_output = qualified_teams[['team_name', 'confederation', 'composite_score', 'rank', 'total.points']].copy()
        qualified_output['status'] = 'Qualified'
        full_48_list.append(qualified_output)
        
        # Add direct projections
        if len(df_direct) > 0:
            direct_for_full = df_direct[['team_name', 'confederation', 'composite_score', 'rank', 'total.points']].copy()
            direct_for_full['status'] = 'Projected (Direct)'
            full_48_list.append(direct_for_full)
        
        # Add playoff winners
        if len(df_playoff_winners) > 0:
            winners_for_full = df_playoff_winners[['team_name', 'confederation', 'composite_score', 'rank', 'total.points']].copy()
            winners_for_full['status'] = 'Projected (Playoff)'
            full_48_list.append(winners_for_full)
        
        # Combine and save
        df_full_48 = pd.concat(full_48_list, ignore_index=True)
        full_path = os.path.join(self.data_processed, 'projected_full_48.csv')
        df_full_48.to_csv(full_path, index=False)
        print(f"   Saved: projected_full_48.csv ({len(df_full_48)} teams)")
        
        # Print confederation distribution
        confed_dist = df_full_48['confederation'].value_counts().to_dict()
        print(f"   Final distribution: {confed_dist}")
        
        print()
        return df_full_48
    
    def generate_report(self, df_master):
        """Generate summary report"""
        print("="*70)
        print(" DATA_100 SCRAPING - SUMMARY REPORT")
        print("="*70)
        print(f"\n Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f" Output Directory: {self.data_processed}")
        
        print(f"\n{'='*70}")
        print(f" OUTPUT FILES")
        print(f"{'='*70}")
        
        output_files = [
            'top100_master_dataset.csv',
            'fifa_rankings_clean.csv',
            'fifa_top100.csv',
            'match_results_clean.csv',
            'match_statistics.csv',
            'qualified_teams_clean.csv',
            'squad_statistics.csv',
            'wc_experience_scores.csv',
            'projected_direct_18.csv',
            'projected_playoff_candidates.csv',
            'projected_playoff_winners.csv',
            'projected_full_48.csv'
        ]
        
        for i, filename in enumerate(output_files, 1):
            filepath = os.path.join(self.data_processed, filename)
            if os.path.exists(filepath):
                size_kb = os.path.getsize(filepath) / 1024
                print(f"{i}.  {filename} ({size_kb:.2f} KB)")
            else:
                print(f"{i}.  {filename} (NOT FOUND)")
        
        print(f"\n{'='*70}")
        print(f" MASTER DATASET SUMMARY")
        print(f"{'='*70}")
        print(f"Shape: {df_master.shape[0]} teams × {df_master.shape[1]} features")
        print(f"Qualified Teams: {df_master['qualified_2026'].sum()}/{len(df_master)}")
        print(f"Missing Values: {df_master.isnull().sum().sum()}")
        print(f"Duplicate Teams: {df_master.duplicated(subset=['team_name']).sum()}")
        
        print(f"\n{'='*70}")
        print(f" SCRAPING COMPLETED SUCCESSFULLY")
        print(f"{'='*70}\n")
    
    def run(self):
        """Run complete scraping pipeline"""
        print(f"\n Starting Data_100 Scraping Pipeline...\n")
        
        # Verify files
        if not self.verify_files():
            print(" ERROR: Some required files are missing!")
            return False
        
        # Scrape each dataset
        df_rankings, df_top100 = self.scrape_rankings()
        df_matches, df_match_stats = self.scrape_matches()
        df_qualified = self.scrape_qualified_teams()
        df_players, df_squad = self.scrape_players()
        df_wc, df_wc_exp = self.scrape_wc_goals()
        
        # Create master dataset
        df_master = self.create_master_dataset(
            df_rankings, df_match_stats, df_qualified, df_squad, df_wc_exp
        )
        
        # Project remaining 20 teams for FIFA 2026
        df_direct, df_playoff_winners = self.project_remaining_20_teams(df_master)
        
        # Generate report
        self.generate_report(df_master)
        
        return True

if __name__ == '__main__':
    # Initialize scraper
    scraper = Data100Scraper(
        data_raw='../Data_100',
        data_processed='../data/processed'
    )
    
    # Run pipeline
    success = scraper.run()
    
    if success:
        print(" All data scraped and processed successfully!")
        print(f" Check output files in: {scraper.data_processed}")
    else:
        print(" Scraping failed. Please check error messages above.")
        sys.exit(1)
