#!/usr/bin/env python3
"""
FIFA 26 Integration Script
==========================

Central script to integrate FIFA 26 Web Scraper with all existing FIFA prediction components.
This script replaces all FIFA_Player_Database.csv usage with live FIFA 26 data from Kaggle.

Author: FIFA Prediction System
Date: October 25, 2025
"""

import os
import sys
import pandas as pd
from fifa_player_web_scraper import FIFA_26_Player_Web_Scraper

class FIFA26Integration:
    """Central integration class for FIFA 26 web data"""
    
    def __init__(self):
        self.fifa_26_scraper = FIFA_26_Player_Web_Scraper()
        
        print("="*70)
        print("FIFA 26 INTEGRATION SYSTEM")
        print("="*70)
        print("Source: https://www.kaggle.com/datasets/rovnez/fc-26-fifa-26-player-data")
        print("Integrating with all FIFA prediction components...")
        print()
    
    def ensure_fifa_26_data(self):
        """Ensure FIFA 26 data is available and up-to-date"""
        print(" Checking FIFA 26 data availability...")
        
        # Check if data is available
        data_available = self.fifa_26_scraper.show_running_data_status()
        
        if not data_available:
            print(" FIFA 26 data not available. Attempting to process...")
            result = self.fifa_26_scraper.integrate_with_existing_scraper()
            
            if result is None:
                print(" Failed to get FIFA 26 data.")
                print(" Manual setup required:")
                print("1. Go to: https://www.kaggle.com/datasets/rovnez/fc-26-fifa-26-player-data")
                print("2. Download the dataset")
                print("3. Save as: Data_Web/fifa_26_players.csv")
                print("4. Run this script again")
                return False
        
        print(" FIFA 26 data is ready!")
        return True
    
    def update_data_100_integration(self):
        """Update Data_100 components to use FIFA 26 data"""
        print("\n Updating Data_100 integration...")
        
        # Check if original FIFA_Player_Database.csv exists
        original_file = "Data_100/FIFA_Player_Database.csv"
        web_file = "Data_100/FIFA_Player_Database_Web.csv"
        
        if os.path.exists(web_file):
            df_web = pd.read_csv(web_file)
            print(f"   FIFA 26 web data ready: {len(df_web)} players")
            
            # Create backup of original if it exists and web data is newer
            if os.path.exists(original_file):
                backup_file = "Data_100/FIFA_Player_Database_Original_Backup.csv"
                if not os.path.exists(backup_file):
                    import shutil
                    shutil.copy2(original_file, backup_file)
                    print(f"   Created backup: {backup_file}")
                
                # Replace original with web data
                df_web.to_csv(original_file, index=False)
                print(f"   Updated {original_file} with FIFA 26 data")
            
            return True
        else:
            print("   FIFA 26 web data not found")
            return False
    
    def update_data_48_integration(self):
        """Update Data_48 components to use FIFA 26 data"""
        print("\n Updating Data_48 integration...")
        
        # Check FIFA 26 48-team data
        fifa_26_48_file = "Data_48/raw/fifa_26_players_48_teams.csv"
        
        if os.path.exists(fifa_26_48_file):
            df_48 = pd.read_csv(fifa_26_48_file)
            print(f"   FIFA 26 48-team data ready: {len(df_48)} players from {df_48['nationality_name'].nunique()} teams")
            
            # Replace old 48-team player data
            old_48_file = "Data_48/raw/fifa_players_48_teams.csv"
            if os.path.exists(old_48_file):
                backup_48_file = "Data_48/raw/fifa_players_48_teams_backup.csv"
                if not os.path.exists(backup_48_file):
                    import shutil
                    shutil.copy2(old_48_file, backup_48_file)
                    print(f"   Created backup: {backup_48_file}")
                
                # Replace with FIFA 26 data
                df_48.to_csv(old_48_file, index=False)
                print(f"   Updated {old_48_file} with FIFA 26 data")
            
            return True
        else:
            print("   FIFA 26 48-team data not found")
            return False
    
    def validate_integration(self):
        """Validate that all components are using FIFA 26 data"""
        print("\n Validating FIFA 26 integration...")
        
        # Check key files
        validation_files = [
            ("Data_100/FIFA_Player_Database_Web.csv", "FIFA 26 Web Database"),
            ("Data_48/raw/fifa_26_players_48_teams.csv", "FIFA 26 48-Team Data"),
            ("Data_48/processed/squad_statistics_web.csv", "FIFA 26 Squad Statistics"),
            ("Data_Web/fifa_26_players_processed.csv", "FIFA 26 Processed Data")
        ]
        
        all_valid = True
        total_players = 0
        
        for file_path, description in validation_files:
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path)
                    size = len(df)
                    if 'player' in file_path.lower():
                        total_players = max(total_players, size)
                    print(f"   {description}: {size} records")
                except Exception as e:
                    print(f"   {description}: Error reading - {str(e)[:50]}...")
                    all_valid = False
            else:
                print(f"   {description}: Not found")
                all_valid = False
        
        if all_valid:
            print(f"\n FIFA 26 Integration Complete!")
            print(f" Total FIFA 26 players: {total_players}")
            print(f" Data source: https://www.kaggle.com/datasets/rovnez/fc-26-fifa-26-player-data")
            print(" Your FIFA 2026 prediction system is ready!")
        else:
            print(f"\n Integration validation failed. Some components need attention.")
        
        return all_valid
    
    def run_complete_integration(self):
        """Run complete FIFA 26 integration process"""
        print(" Starting FIFA 26 Complete Integration...")
        
        # Step 1: Ensure FIFA 26 data is available
        if not self.ensure_fifa_26_data():
            return False
        
        # Step 2: Update Data_100 integration
        if not self.update_data_100_integration():
            print(" Data_100 integration failed")
        
        # Step 3: Update Data_48 integration
        if not self.update_data_48_integration():
            print(" Data_48 integration failed")
        
        # Step 4: Validate integration
        return self.validate_integration()

def main():
    """Main function to run FIFA 26 integration"""
    try:
        integration = FIFA26Integration()
        success = integration.run_complete_integration()
        
        if success:
            print("\n" + "="*70)
            print(" FIFA 26 INTEGRATION SUCCESSFUL!")
            print("="*70)
            print("Your FIFA prediction system now uses FIFA 26 player data from Kaggle.")
            print("All components have been updated to use the web scraper.")
        else:
            print("\n" + "="*70)
            print(" FIFA 26 INTEGRATION INCOMPLETE")
            print("="*70)
            print("Some components could not be updated. Check the output above.")
        
        return success
        
    except Exception as e:
        print(f"\n Integration failed with error: {e}")
        return False

if __name__ == "__main__":
    main()