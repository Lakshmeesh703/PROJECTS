import pandas as pd
import requests
from io import StringIO
import os
import time
import zipfile
from urllib.parse import urlparse
import json
import warnings

# Suppress DtypeWarning for mixed types in CSV columns
warnings.filterwarnings('ignore', category=pd.errors.DtypeWarning)

class FIFA_26_Player_Web_Scraper:
    """
    Web scraper to replace FIFA_Player_Database.csv with live Kaggle FIFA 26 data
    Enhanced with Kaggle API integration
    """
    
    def __init__(self, data_raw="Data_100", data_processed="Data_48/processed", kaggle_json_path=None):
        # Update paths to work with new project structure
        # Get project root (two levels up from TASK_1_Data_Collection/scripts/)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
        
        # New folder structure paths
        self.data_raw = os.path.join(self.project_root, "TASK_1_Data_Collection", "data", "sources")
        self.data_processed = os.path.join(self.project_root, "TASK_2_Data_Preprocessing", "data", "processed")
        self.data_web = os.path.join(self.project_root, "shared_data", "player_data")
        self.data_squad = os.path.join(self.project_root, "shared_data", "squad_data")
        
        # Create output directories
        os.makedirs(self.data_raw, exist_ok=True)
        os.makedirs(self.data_processed, exist_ok=True)
        os.makedirs(self.data_web, exist_ok=True)
        os.makedirs(self.data_squad, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Kaggle dataset info
        self.kaggle_url = "https://www.kaggle.com/datasets/rovnez/fc-26-fifa-26-player-data"
        self.dataset_owner = "rovnez"
        self.dataset_name = "fc-26-fifa-26-player-data"
        
        # Load Kaggle API credentials
        self.kaggle_username = None
        self.kaggle_key = None
        self.load_kaggle_credentials(kaggle_json_path)
    
    def load_kaggle_credentials(self, kaggle_json_path=None):
        """
        Load Kaggle API credentials from kaggle.json file
        """
        try:
            # Priority 1: Use provided path
            if kaggle_json_path and os.path.exists(kaggle_json_path):
                with open(kaggle_json_path, 'r') as f:
                    creds = json.load(f)
                    self.kaggle_username = creds.get('username')
                    self.kaggle_key = creds.get('key')
                    print(f"   Loaded Kaggle credentials from: {kaggle_json_path}")
                    return
            
            # Priority 2: Look in Downloads folder
            downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'kaggle (1).json')
            if os.path.exists(downloads_path):
                with open(downloads_path, 'r') as f:
                    creds = json.load(f)
                    self.kaggle_username = creds.get('username')
                    self.kaggle_key = creds.get('key')
                    print(f"   Loaded Kaggle credentials from Downloads folder")
                    return
            
            # Priority 3: Standard Kaggle location
            kaggle_dir = os.path.join(os.path.expanduser('~'), '.kaggle')
            kaggle_json = os.path.join(kaggle_dir, 'kaggle.json')
            if os.path.exists(kaggle_json):
                with open(kaggle_json, 'r') as f:
                    creds = json.load(f)
                    self.kaggle_username = creds.get('username')
                    self.kaggle_key = creds.get('key')
                    print(f"   Loaded Kaggle credentials from ~/.kaggle/kaggle.json")
                    return
            
            # Priority 4: Environment variables
            self.kaggle_username = os.environ.get('KAGGLE_USERNAME')
            self.kaggle_key = os.environ.get('KAGGLE_KEY')
            if self.kaggle_username and self.kaggle_key:
                print(f"   Loaded Kaggle credentials from environment variables")
                return
            
            print("   No Kaggle credentials found - will use fallback methods")
            
        except Exception as e:
            print(f"   Failed to load Kaggle credentials: {e}")
    
    def download_with_kaggle_api(self):
        """
        Download dataset using Kaggle API with authentication
        """
        if not self.kaggle_username or not self.kaggle_key:
            print("   Kaggle API credentials not available")
            return None
        
        try:
            print(f"   Authenticating with Kaggle API as: {self.kaggle_username}")
            
            # Try using kaggle library if installed
            try:
                from kaggle.api.kaggle_api_extended import KaggleApi
                
                api = KaggleApi()
                api.authenticate()
                
                # Download dataset
                dataset_path = f"{self.dataset_owner}/{self.dataset_name}"
                download_dir = "Data_Web"
                
                print(f"   Downloading from Kaggle: {dataset_path}")
                api.dataset_download_files(dataset_path, path=download_dir, unzip=True)
                
                # Find the downloaded CSV file
                csv_files = [f for f in os.listdir(download_dir) if f.endswith('.csv')]
                if csv_files:
                    csv_file = os.path.join(download_dir, csv_files[0])
                    print(f"   Downloaded: {csv_file}")
                    df = pd.read_csv(csv_file)
                    
                    # Save as standard name
                    standard_path = os.path.join(download_dir, "fifa_26_players.csv")
                    df.to_csv(standard_path, index=False)
                    
                    return df
                
            except ImportError:
                print("   kaggle library not installed, using direct API")
                return self.download_with_direct_api()
            
        except Exception as e:
            print(f"   Kaggle API download failed: {e}")
            return None
    
    def download_with_direct_api(self):
        """
        Download using direct HTTP requests with Kaggle API authentication
        """
        try:
            # Kaggle API endpoint
            api_url = f"https://www.kaggle.com/api/v1/datasets/download/{self.dataset_owner}/{self.dataset_name}"
            
            print(f"   Using Kaggle API: {api_url}")
            
            # Make authenticated request
            response = self.session.get(
                api_url,
                auth=(self.kaggle_username, self.kaggle_key),
                stream=True,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"   API response successful (200 OK)")
                
                # Check if ZIP file
                content_type = response.headers.get('Content-Type', '')
                if 'zip' in content_type or response.content[:2] == b'PK':
                    print("   Extracting ZIP archive...")
                    df = self.extract_csv_from_zip(response.content)
                    if df is not None:
                        # Save the downloaded data
                        output_path = os.path.join("Data_Web", "fifa_26_players.csv")
                        df.to_csv(output_path, index=False)
                        print(f"   Saved to: {output_path}")
                        return df
                else:
                    # Direct CSV response
                    df = pd.read_csv(StringIO(response.text))
                    output_path = os.path.join("Data_Web", "fifa_26_players.csv")
                    df.to_csv(output_path, index=False)
                    print(f"   Saved to: {output_path}")
                    return df
            else:
                print(f"   API request failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   Direct API download failed: {e}")
        
        return None
        
    def get_kaggle_direct_download_url(self):
        """
        Get the specific Kaggle download URL only
        """
        # Use only the exact URL specified by user
        kaggle_download_url = "https://www.kaggle.com/datasets/rovnez/fc-26-fifa-26-player-data/download"
        
        # Return only this specific URL
        return [kaggle_download_url]
    
    def scrape_fifa_26_players_from_kaggle(self):
        """
        Use running FIFA 26 player data from available sources
        """
        print(" Loading FIFA Player Data from Running Sources...")
        print(f" Target: FIFA 26 data from Kaggle source")
        
        try:
            # Use existing running data instead of downloading
            df_players = self.download_kaggle_dataset()
            
            if df_players is not None and len(df_players) > 0:
                print(f"   Using {len(df_players)} players from running data")
                
                # Check if data needs processing or is already processed
                required_columns = ['player_name', 'nationality_name', 'overall']
                if all(col in df_players.columns for col in required_columns):
                    print("   Data already processed, using directly")
                    df_processed = df_players
                else:
                    print("   Processing raw data...")
                    df_processed = self.process_fifa_26_data(df_players)
                
                # Validate processed data
                if len(df_processed) < 100:
                    print(f"   Processed data too small ({len(df_processed)} players)")
                    return None, None
                
                # Save processed data (update running data)
                self.save_processed_data(df_processed)
                
                # Create 48-team focused version
                df_48_teams = self.filter_to_48_teams(df_processed)
                
                return df_processed, df_48_teams
            else:
                print("   No running data available")
                return None, None
                
        except Exception as e:
            import traceback
            print(f"   Failed to use running data: {e}")
            print(f"   Full error:")
            traceback.print_exc()
            return None, None
    
    def download_kaggle_dataset(self):
        """
        Use existing data - SKIP downloading to save time
        """
        print("   Loading existing FIFA 26 data (skip download)...")
        
        # Priority 1: Use already processed data
        processed_file = os.path.join(self.data_web, "fifa_26_players_processed.csv")
        if os.path.exists(processed_file):
            print(f"   Found processed data: {processed_file}")
            try:
                df_processed = pd.read_csv(processed_file)
                print(f"     Loaded {len(df_processed)} players")
                return df_processed
            except Exception as e:
                print(f"     Error: {e}")
        
        # Priority 2: Use existing download
        manual_file = os.path.join(self.data_web, "fifa_26_players.csv")
        if os.path.exists(manual_file):
            print(f"   Found existing data: {manual_file}")
            try:
                df_manual = pd.read_csv(manual_file)
                print(f"     Loaded {len(df_manual)} players")
                return df_manual
            except Exception as e:
                print(f"     Error: {e}")
        
        # Priority 3: Use web database
        web_database_file = os.path.join(self.data_raw, "FIFA_Player_Database_Web.csv")
        if os.path.exists(web_database_file):
            print(f"   Found web database: {web_database_file}")
            try:
                df_web = pd.read_csv(web_database_file)
                print(f"     Loaded {len(df_web)} players")
                return df_web
            except Exception as e:
                print(f"     Error: {e}")
        
        # Priority 4: Use 48-team data
        teams_48_file = os.path.join(self.data_processed, "fifa_26_players_48_teams.csv")
        if os.path.exists(teams_48_file):
            print(f"   Found 48-team data: {teams_48_file}")
            try:
                df_48 = pd.read_csv(teams_48_file)
                print(f"     Loaded {len(df_48)} players")
                return df_48
            except Exception as e:
                print(f"     Error: {e}")
        
        # If no data found, provide instructions
        print("\n   No data found. Setup instructions:")
        if not self.kaggle_username or not self.kaggle_key:
            print("   OPTION 1: Set up Kaggle API (RECOMMENDED)")
            print("     1. Kaggle API token detected in Downloads folder!")
            print("     2. Install kaggle package: pip install kaggle")
            print("     3. Re-run this script - it will auto-download the data!")
        print("   OPTION 2: Manual download")
        print("     1. Go to: https://www.kaggle.com/datasets/rovnez/fc-26-fifa-26-player-data")
        print("     2. Click 'Download' button")
        print(f"     3. Extract ZIP and save CSV as: {os.path.join(self.data_web, 'fifa_26_players.csv')}")
        
        return None
    
    def extract_csv_from_zip(self, zip_content):
        """
        Extract CSV from ZIP file content
        """
        try:
            import zipfile
            from io import BytesIO
            
            print("     Extracting CSV from ZIP file...")
            
            with zipfile.ZipFile(BytesIO(zip_content)) as zip_file:
                # List all files in the ZIP
                file_list = zip_file.namelist()
                print(f"     Files in ZIP: {file_list}")
                
                # Look for CSV files
                csv_files = [f for f in file_list if f.endswith('.csv')]
                
                if csv_files:
                    # Use the first (or largest) CSV file
                    csv_file = csv_files[0]
                    print(f"     Extracting: {csv_file}")
                    
                    with zip_file.open(csv_file) as csv_data:
                        df = pd.read_csv(csv_data)
                        print(f"     Extracted {len(df)} players from {csv_file}")
                        return df
                else:
                    print("     No CSV files found in ZIP")
                    return None
                    
        except Exception as e:
            print(f"     ZIP extraction failed: {e}")
            return None
    
    def process_fifa_26_data(self, df_raw):
        """
        Process raw FIFA 26 data to match your existing structure
        """
        print("   Processing FIFA 26 player data...")
        
        # Check available columns
        print(f"     Raw columns: {list(df_raw.columns)}")
        
        # Enhanced column mappings for various FIFA datasets
        # Build rename dictionary only for columns that exist
        df_processed = df_raw.copy()
        
        rename_map = {}
        # Priority order for name columns
        if 'short_name' in df_processed.columns and 'player_name' not in df_processed.columns:
            rename_map['short_name'] = 'player_name'
        elif 'long_name' in df_processed.columns and 'player_name' not in df_processed.columns and 'short_name' not in df_processed.columns:
            rename_map['long_name'] = 'player_name'
        elif 'Name' in df_processed.columns and 'player_name' not in df_processed.columns:
            rename_map['Name'] = 'player_name'
        
        # Nationality
        if 'nationality_name' not in df_processed.columns:
            if 'Nationality' in df_processed.columns:
                rename_map['Nationality'] = 'nationality_name'
            elif 'nationality' in df_processed.columns:
                rename_map['nationality'] = 'nationality_name'
        
        # Stats - only rename if target doesn't exist
        stat_mappings = {
            'Overall': 'overall', 'Potential': 'potential', 'Age': 'age',
            'Pace': 'pace', 'Shooting': 'shooting', 'Passing': 'passing',
            'Dribbling': 'dribbling', 'Defending': 'defending', 
            'Physical': 'physic', 'Physicality': 'physic'
        }
        
        for old_col, new_col in stat_mappings.items():
            if old_col in df_processed.columns and new_col not in df_processed.columns:
                rename_map[old_col] = new_col
        
        # Apply renames
        if rename_map:
            df_processed.rename(columns=rename_map, inplace=True)
            for old, new in rename_map.items():
                print(f"       Mapped '{old}' → '{new}'")
        
        # Ensure required columns exist
        required_columns = ['player_name', 'nationality_name', 'overall']
        missing_columns = [col for col in required_columns if col not in df_processed.columns]
        
        if missing_columns:
            print(f"     Missing required columns: {missing_columns}")
            # Try to create or estimate missing columns
            df_processed = self.handle_missing_columns(df_processed, missing_columns)
        
        # Clean and standardize data
        df_processed = self.clean_player_data(df_processed)
        
        print(f"     Processed {len(df_processed)} players")
        return df_processed
    
    def handle_missing_columns(self, df, missing_columns):
        """
        Handle missing columns by estimation or creation
        """
        for col in missing_columns:
            if col == 'player_name' and 'Name' not in df.columns:
                # If no name column, create dummy names
                df['player_name'] = [f"Player_{i}" for i in range(len(df))]
            elif col == 'nationality_name':
                # Try to find any country/nation column
                possible_nation_cols = [c for c in df.columns if 'nation' in c.lower() or 'country' in c.lower()]
                if possible_nation_cols:
                    df['nationality_name'] = df[possible_nation_cols[0]]
                else:
                    df['nationality_name'] = 'Unknown'
            elif col == 'overall':
                # Estimate overall from other ratings if available
                rating_cols = [c for c in df.columns if any(skill in c.lower() for skill in ['pace', 'shoot', 'pass', 'dribbl', 'defend', 'physic'])]
                if rating_cols:
                    df['overall'] = df[rating_cols].mean(axis=1).round()
                else:
                    df['overall'] = 70  # Default rating
        
        return df
    
    def clean_player_data(self, df):
        """
        Clean and standardize player data
        """
        # Standardize nationality names to match your existing data
        if 'nationality_name' in df.columns:
            nationality_mappings = {
                'South Korea': 'Korea Republic',
                'Ivory Coast': "Côte d'Ivoire",
                'Czech Republic': 'Czechia',
                'United States': 'United States of America',
                # Add more mappings as needed
            }
            
            # Apply mappings row by row
            for old_name, new_name in nationality_mappings.items():
                df.loc[df['nationality_name'] == old_name, 'nationality_name'] = new_name
        
        # Ensure numeric columns - only process columns that exist and are Series
        numeric_columns = ['overall', 'potential', 'age', 'pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic']
        for col in numeric_columns:
            if col in df.columns and not df[col].empty:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except Exception as e:
                    print(f"       Could not convert {col} to numeric: {e}")
        
        # Remove rows with invalid data
        if 'overall' in df.columns:
            df = df.dropna(subset=['overall'])
            df = df[df['overall'] > 0]
        
        # Sort by overall rating (best players first)
        if 'overall' in df.columns:
            df = df.sort_values('overall', ascending=False).reset_index(drop=True)
        
        return df
    
    def save_processed_data(self, df_processed):
        """
        Save processed data to replace your original CSV
        """
        # Save as replacement for FIFA_Player_Database.csv
        output_original = os.path.join(self.data_raw, "FIFA_Player_Database_Web.csv")
        df_processed.to_csv(output_original, index=False)
        print(f"     Saved web version: {output_original}")
        
        # Save in shared_data/player_data folder
        output_web = os.path.join(self.data_web, "fifa_26_players_processed.csv")
        df_processed.to_csv(output_web, index=False)
        print(f"     Saved processed: {output_web}")
        
        return output_original
    
    def filter_to_48_teams(self, df_players):
        """
        Filter players to only those from FIFA 2026 World Cup teams (48 teams)
        """
        print("   Filtering to FIFA 2026 World Cup teams...")
        
        # Load your 48 FIFA 2026 teams
        try:
            teams_file = os.path.join(self.data_processed, "projected_full_48.csv")
            df_48_teams = pd.read_csv(teams_file)
            team_list_48 = df_48_teams['team_name'].tolist()
            print(f"     Loaded FIFA 2026 teams from file: {len(team_list_48)}")
        except Exception as e:
            print(f"     Could not load 48 teams file: {e}")
            # Use the complete list of 48 FIFA 2026 World Cup teams
            team_list_48 = [
                # CONCACAF (8 teams)
                'USA', 'Mexico', 'Canada', 'Costa Rica', 'Panama', 'Jamaica', 'Honduras', 'Guatemala',
                
                # CONMEBOL (6 teams) 
                'Argentina', 'Brazil', 'Uruguay', 'Colombia', 'Chile', 'Ecuador',
                
                # UEFA (16 teams)
                'France', 'Spain', 'England', 'Portugal', 'Netherlands', 'Belgium', 'Italy', 'Germany',
                'Croatia', 'Denmark', 'Switzerland', 'Austria', 'Poland', 'Ukraine', 'Sweden', 'Norway',
                
                # CAF (9 teams)
                'Morocco', 'Senegal', 'Tunisia', 'Algeria', 'Egypt', 'Nigeria', 'Ghana', 'Cameroon', 'Mali',
                
                # AFC (8 teams)
                'Japan', 'Korea Republic', 'Australia', 'IR Iran', 'Saudi Arabia', 'Qatar', 'UAE', 'Iraq',
                
                # OFC (1 team)
                'New Zealand'
            ]
            print(f"     Using default FIFA 2026 teams: {len(team_list_48)}")
        
        # Check which teams are available in the dataset
        available_teams = set(df_players['nationality_name'].unique())
        found_teams = set(team_list_48) & available_teams
        missing_teams = set(team_list_48) - available_teams
        
        print(f"     Found {len(found_teams)} out of 48 World Cup teams in dataset")
        if missing_teams:
            print(f"     Missing teams: {sorted(list(missing_teams))}")
        
        # Filter players by nationality
        df_48_players = df_players[df_players['nationality_name'].isin(team_list_48)]
        
        # Save 48-team player data
        output_48 = os.path.join(self.data_processed, "fifa_26_players_48_teams.csv")
        df_48_players.to_csv(output_48, index=False)
        
        print(f"     FIFA 2026 players: {len(df_48_players)} (from {df_48_players['nationality_name'].nunique()} teams)")
        print(f"     Saved: {output_48}")
        
        # Show team distribution
        team_counts = df_48_players['nationality_name'].value_counts()
        print(f"     Top 5 teams by player count:")
        for team, count in team_counts.head().items():
            print(f"      • {team}: {count} players")
        
        return df_48_players
    
    def fallback_to_local_data(self):
        """
        Fallback to existing local CSV if web scraping fails
        """
        print("   Falling back to local player data...")
        
        try:
            local_file = os.path.join(self.data_raw, "FIFA_Player_Database.csv")
            if os.path.exists(local_file):
                df_local = pd.read_csv(local_file)
                print(f"     Loaded local players: {len(df_local)}")
                return df_local, None
            else:
                print(f"     Local file not found: {local_file}")
                return None, None
        except Exception as e:
            print(f"     Local fallback failed: {e}")
            return None, None
    
    def integrate_with_existing_scraper(self):
        """
        Integration method using running FIFA 26 data
        """
        print(" Integrating FIFA 26 running data with existing pipeline...")
        
        # Use running data instead of scraping
        df_all_players, df_48_players = self.scrape_fifa_26_players_from_kaggle()
        
        if df_all_players is not None:
            # Calculate squad statistics (like your existing method) 
            df_for_stats = df_48_players if df_48_players is not None else df_all_players
            squad_stats = self.calculate_squad_statistics(df_for_stats)
            
            # Save squad statistics
            output_stats = os.path.join(self.data_squad, 'squad_statistics_web.csv')
            squad_stats.to_csv(output_stats, index=False)
            print(f"   Squad statistics: {output_stats}")
            
            return squad_stats
        
        return None
    
    def calculate_squad_statistics(self, df_players):
        """
        Calculate squad statistics (same logic as your existing scraper)
        """
        if df_players is None or len(df_players) == 0:
            return pd.DataFrame()
        
        # Ensure required columns exist with default values
        for col in ['potential', 'age', 'pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic']:
            if col not in df_players.columns:
                df_players[col] = 70 if col != 'age' else 25
        
        # Convert numeric columns to numeric type (handle mixed types)
        numeric_cols = ['overall', 'potential', 'age', 'pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic']
        for col in numeric_cols:
            if col in df_players.columns:
                df_players.loc[:, col] = pd.to_numeric(df_players[col], errors='coerce')
        
        # Group by nationality and calculate stats
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
        squad_stats.columns = [
            'avg_overall', 'max_overall', 'squad_size', 'avg_potential',
            'avg_age', 'avg_pace', 'avg_shooting', 'avg_passing',
            'avg_dribbling', 'avg_defending', 'avg_physic'
        ]
        
        # Reset index
        squad_stats = squad_stats.reset_index()
        squad_stats.rename(columns={'nationality_name': 'team_name'}, inplace=True)
        
        return squad_stats

    def show_running_data_status(self):
        """
        Show status of available running data
        """
        print(" RUNNING DATA STATUS:")
        print("="*50)
        
        data_sources = [
            ("Processed Data", os.path.join(self.data_web, "fifa_26_players_processed.csv"), " Ready to use"),
            ("Raw Manual Data", os.path.join(self.data_web, "fifa_26_players.csv"), " Needs processing"),
            ("Web Database", os.path.join(self.data_raw, "FIFA_Player_Database_Web.csv"), " Ready to use"),
            ("48-Team Data", os.path.join(self.data_processed, "fifa_26_players_48_teams.csv"), " Ready to use"),
            ("Squad Statistics", os.path.join(self.data_squad, "squad_statistics_web.csv"), " Analytics ready")
        ]
        
        available_sources = 0
        total_players = 0
        
        for name, file_path, status in data_sources:
            if os.path.exists(file_path):
                try:
                    if file_path.endswith('.csv'):
                        df = pd.read_csv(file_path)
                        size = len(df)
                        if 'player' in file_path.lower() or 'database' in file_path.lower():
                            total_players = max(total_players, size)
                        print(f"   {name}: {size} records | {status}")
                        available_sources += 1
                    else:
                        print(f"   {name}: Available | {status}")
                        available_sources += 1
                except Exception as e:
                    print(f"   {name}: File exists but error reading: {str(e)[:30]}...")
            else:
                print(f"   {name}: Not available")
        
        print(f"\n SUMMARY:")
        print(f"  • Available data sources: {available_sources}/5")
        print(f"  • Total FIFA players: {total_players}")
        print(f"  • Data source: https://www.kaggle.com/datasets/rovnez/fc-26-fifa-26-player-data")
        print(f"  • Status: {' Fully operational' if available_sources >= 3 else ' Partially available' if available_sources > 0 else ' No data available'}")
        
        return available_sources >= 3

# Usage function
def run_fifa_26_web_scraping(kaggle_json_path=None):
    """
    Main function to run FIFA 26 data processing with Kaggle API support
    
    Args:
        kaggle_json_path: Optional path to kaggle.json file (default: auto-detect)
    """
    print("="*70)
    print(" FIFA 26 DATA PROCESSOR WITH KAGGLE API")
    print("="*70)
    
    # Auto-detect kaggle.json in Downloads if not provided
    if kaggle_json_path is None:
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'kaggle (1).json')
        if os.path.exists(downloads_path):
            kaggle_json_path = downloads_path
            print(f" Auto-detected Kaggle credentials in Downloads folder")
    
    # Initialize scraper with Kaggle API support
    scraper = FIFA_26_Player_Web_Scraper(kaggle_json_path=kaggle_json_path)
    
    # Show running data status first
    data_available = scraper.show_running_data_status()
    print()
    
    # Run the data processing (will try Kaggle API if credentials available)
    result = scraper.integrate_with_existing_scraper()
    
    if result is not None:
        print("\n FIFA 26 Data Processing completed successfully!")
        print(" Files updated:")
        print(f"  • {os.path.join('shared_data', 'player_data', 'fifa_26_players_processed.csv')}")
        print(f"  • {os.path.join('TASK_1_Data_Collection', 'data', 'sources', 'FIFA_Player_Database_Web.csv')}")
        print(f"  • {os.path.join('TASK_2_Data_Preprocessing', 'data', 'processed', 'fifa_26_players_48_teams.csv')}")
        print(f"  • {os.path.join('shared_data', 'squad_data', 'squad_statistics_web.csv')}")
        print("\n Your FIFA 2026 prediction system is ready!")
    else:
        print("\n Data processing completed with existing data")
        if not data_available:
            print(" To get fresh data:")
            if scraper.kaggle_username:
                print("   Install Kaggle library: pip install kaggle")
                print("   Re-run this script for automatic download")
            else:
                print("   Download from: https://www.kaggle.com/datasets/rovnez/fc-26-fifa-26-player-data")
                print("   Save as: Data_Web/fifa_26_players.csv")
    
    return result
    
    if result is not None:
        print("\n FIFA 26 Data Processing completed successfully!")
        print(" Files updated:")
        print(f"  • {os.path.join('shared_data', 'player_data', 'fifa_26_players_processed.csv')}")
        print(f"  • {os.path.join('TASK_1_Data_Collection', 'data', 'sources', 'FIFA_Player_Database_Web.csv')}")
        print(f"  • {os.path.join('TASK_2_Data_Preprocessing', 'data', 'processed', 'fifa_26_players_48_teams.csv')}")
        print(f"  • {os.path.join('shared_data', 'squad_data', 'squad_statistics_web.csv')}")
        print("\n Your FIFA 2026 prediction system is ready!")
    else:
        print("\n Data processing failed. Check data status.")
    
    return result

if __name__ == "__main__":
    run_fifa_26_web_scraping()