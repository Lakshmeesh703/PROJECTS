"""
Update this file in TASK_1_Data_Collection/scripts/fifa_player_web_scraper.py
Replace the __init__ method's credential loading section with this:
"""

def __init__(self, data_raw="Data_100", data_processed="Data_48/processed", kaggle_username=None, kaggle_key=None):
    """
    Initialize FIFA 26 Player Web Scraper
    
    Args:
        data_raw: Directory for raw data
        data_processed: Directory for processed data  
        kaggle_username: Kaggle username (from env variable)
        kaggle_key: Kaggle API key (from env variable)
    """
    import os
    
    # Calculate project root and data paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    self.project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    
    # Set up data directories
    self.data_raw = os.path.join(self.project_root, "TASK_1_Data_Collection", "data", "sources")
    self.data_processed = os.path.join(self.project_root, "TASK_2_Data_Preprocessing", "data", "processed")
    self.data_web = os.path.join(self.project_root, "shared_data", "player_data")
    self.data_squad = os.path.join(self.project_root, "shared_data", "squad_data")
    
    # Create directories
    for directory in [self.data_raw, self.data_processed, self.data_web, self.data_squad]:
        os.makedirs(directory, exist_ok=True)
    
    # Kaggle configuration
    self.kaggle_dataset = "rovnez/fc-26-fifa-26-player-data"
    
    # Try to get Kaggle credentials from environment variables first (for deployment)
    self.kaggle_username = kaggle_username or os.environ.get('KAGGLE_USERNAME')
    self.kaggle_key = kaggle_key or os.environ.get('KAGGLE_KEY')
    
    # If not in environment, try to load from file (for local development)
    if not self.kaggle_username or not self.kaggle_key:
        self._load_kaggle_credentials_from_file()
    
    # Set up Kaggle API
    if self.kaggle_username and self.kaggle_key:
        os.environ['KAGGLE_USERNAME'] = self.kaggle_username
        os.environ['KAGGLE_KEY'] = self.kaggle_key
        print("   Loaded Kaggle credentials successfully")
    else:
        print("   Warning: Kaggle credentials not found. Scraping may fail.")

def _load_kaggle_credentials_from_file(self):
    """Load Kaggle credentials from kaggle.json file (local development only)"""
    import json
    import os
    
    # Check common locations
    possible_paths = [
        os.path.expanduser("~/.kaggle/kaggle.json"),
        os.path.expanduser("~/Downloads/kaggle.json"),
        os.path.expanduser("~/Downloads/kaggle (1).json"),
        os.path.join(os.getcwd(), "kaggle.json")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    credentials = json.load(f)
                    self.kaggle_username = credentials.get('username')
                    self.kaggle_key = credentials.get('key')
                    print(f"   Loaded Kaggle credentials from: {path}")
                    return
            except Exception as e:
                print(f"   Error reading {path}: {e}")
    
    print("   No kaggle.json file found in common locations")
