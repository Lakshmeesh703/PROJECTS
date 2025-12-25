"""
FIFA 2026 Data Loader - Integrates scraped player data with team rankings
Loads real data from CSV files and runs web scraper for fresh data
"""

import pandas as pd
import os
import numpy as np
import sys

# Import the FIFA 26 web scraper
SCRAPER_AVAILABLE = False
try:
    # Add the scraper directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    scraper_dir = os.path.join(current_dir, "..", "..", "TASK_1_Data_Collection", "scripts")
    if os.path.exists(scraper_dir):
        sys.path.insert(0, scraper_dir)
        from fifa_player_web_scraper import FIFA_26_Player_Web_Scraper  # type: ignore
        SCRAPER_AVAILABLE = True
except ImportError as e:
    SCRAPER_AVAILABLE = False
    print(f"Web scraper not available, using cached data")

class FIFA2026DataLoader:
    """Load and process FIFA 2026 data from scraped sources"""
    
    def __init__(self, auto_scrape=True):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up to project root (from TASK_6_Deployment/app to project root)
        self.project_root = os.path.join(self.base_dir, "..", "..")
        
        # File paths for scraped data (now in shared_data)
        self.rankings_file = os.path.join(self.project_root, "TASK_2_Data_Preprocessing", "data", "processed", "fifa_top100.csv")
        self.player_data_file = os.path.join(self.project_root, "shared_data", "player_data", "fifa_26_players_processed.csv")
        self.squad_stats_file = os.path.join(self.project_root, "shared_data", "squad_data", "squad_statistics_web.csv")
        
        # Initialize web scraper if available
        self.scraper = None
        if SCRAPER_AVAILABLE and auto_scrape:
            print(" Initializing FIFA 26 Web Scraper...")
            try:
                self.scraper = FIFA_26_Player_Web_Scraper()
                self.refresh_player_data()
            except Exception as e:
                print(f" Web scraper initialization failed: {e}")
                print(" Will use cached data instead")
        
        # FIFA 2026 World Cup 48 teams (qualified + projected)
        # Updated with 28 officially qualified teams from qualified_teams_clean.csv
        self.wc_2026_teams = {
            # CONCACAF (8 teams) - 3 Qualified + 5 Projected
            'USA': {'confederation': 'CONCACAF', 'status': 'Qualified'},
            'Mexico': {'confederation': 'CONCACAF', 'status': 'Qualified'},
            'Canada': {'confederation': 'CONCACAF', 'status': 'Qualified'},
            'Costa Rica': {'confederation': 'CONCACAF', 'status': 'Projected'},
            'Panama': {'confederation': 'CONCACAF', 'status': 'Projected'},
            'Jamaica': {'confederation': 'CONCACAF', 'status': 'Projected'},
            'Honduras': {'confederation': 'CONCACAF', 'status': 'Projected'},
            'Guatemala': {'confederation': 'CONCACAF', 'status': 'Projected'},
            
            # CONMEBOL (6 teams) - 6 Qualified
            'Argentina': {'confederation': 'CONMEBOL', 'status': 'Qualified'},
            'Brazil': {'confederation': 'CONMEBOL', 'status': 'Qualified'},
            'Uruguay': {'confederation': 'CONMEBOL', 'status': 'Qualified'},
            'Colombia': {'confederation': 'CONMEBOL', 'status': 'Qualified'},
            'Ecuador': {'confederation': 'CONMEBOL', 'status': 'Qualified'},
            'Paraguay': {'confederation': 'CONMEBOL', 'status': 'Qualified'},
            
            # UEFA (16 teams) - ONLY 1 Qualified (England)
            'England': {'confederation': 'UEFA', 'status': 'Qualified'},
            'France': {'confederation': 'UEFA', 'status': 'Projected'},
            'Spain': {'confederation': 'UEFA', 'status': 'Projected'},
            'Portugal': {'confederation': 'UEFA', 'status': 'Projected'},
            'Netherlands': {'confederation': 'UEFA', 'status': 'Projected'},
            'Belgium': {'confederation': 'UEFA', 'status': 'Projected'},
            'Italy': {'confederation': 'UEFA', 'status': 'Projected'},
            'Germany': {'confederation': 'UEFA', 'status': 'Projected'},
            'Croatia': {'confederation': 'UEFA', 'status': 'Projected'},
            'Denmark': {'confederation': 'UEFA', 'status': 'Projected'},
            'Switzerland': {'confederation': 'UEFA', 'status': 'Projected'},
            'Austria': {'confederation': 'UEFA', 'status': 'Projected'},
            'Poland': {'confederation': 'UEFA', 'status': 'Projected'},
            'Ukraine': {'confederation': 'UEFA', 'status': 'Projected'},
            'Sweden': {'confederation': 'UEFA', 'status': 'Projected'},
            'Norway': {'confederation': 'UEFA', 'status': 'Projected'},
            
            # CAF (9 teams) - ALL 9 Qualified
            'Morocco': {'confederation': 'CAF', 'status': 'Qualified'},
            'Senegal': {'confederation': 'CAF', 'status': 'Qualified'},
            'Tunisia': {'confederation': 'CAF', 'status': 'Qualified'},
            'Algeria': {'confederation': 'CAF', 'status': 'Qualified'},
            'Egypt': {'confederation': 'CAF', 'status': 'Qualified'},
            'Ghana': {'confederation': 'CAF', 'status': 'Qualified'},
            'Cabo Verde': {'confederation': 'CAF', 'status': 'Qualified'},
            'South Africa': {'confederation': 'CAF', 'status': 'Qualified'},
            'Côte d\'Ivoire': {'confederation': 'CAF', 'status': 'Qualified'},
            
            # AFC (8 teams) - ALL 8 Qualified
            'Japan': {'confederation': 'AFC', 'status': 'Qualified'},
            'Korea Republic': {'confederation': 'AFC', 'status': 'Qualified'},
            'Australia': {'confederation': 'AFC', 'status': 'Qualified'},
            'IR Iran': {'confederation': 'AFC', 'status': 'Qualified'},
            'Saudi Arabia': {'confederation': 'AFC', 'status': 'Qualified'},
            'Qatar': {'confederation': 'AFC', 'status': 'Qualified'},
            'Jordan': {'confederation': 'AFC', 'status': 'Qualified'},
            'Uzbekistan': {'confederation': 'AFC', 'status': 'Qualified'},
            
            # OFC (1 team) - 1 Qualified
            'New Zealand': {'confederation': 'OFC', 'status': 'Qualified'}
        }
    
    def refresh_player_data(self):
        """
        Refresh player data using web scraper
        """
        if not self.scraper:
            print(" Web scraper not initialized")
            return False
        
        try:
            print(" Scraping fresh FIFA 26 player data...")
            
            # Run the scraper integration
            result = self.scraper.integrate_with_existing_scraper()
            
            if result is not None:
                print(" Fresh player data scraped successfully!")
                return True
            else:
                print(" Scraping completed, using existing data")
                return False
                
        except Exception as e:
            print(f" Scraping failed: {e}")
            print(" Falling back to cached data")
            return False
    
    def load_fifa_rankings(self):
        """Load FIFA rankings from scraped data"""
        try:
            df = pd.read_csv(self.rankings_file)
            print(f" Loaded FIFA rankings: {len(df)} teams")
            return df
        except Exception as e:
            print(f" Could not load rankings: {e}")
            return None
    
    def load_player_data(self):
        """Load player data from scraped FIFA 26 database"""
        try:
            df = pd.read_csv(self.player_data_file)
            print(f" Loaded player data: {len(df)} players")
            return df
        except Exception as e:
            print(f" Could not load player data: {e}")
            return None
    
    def load_squad_statistics(self):
        """Load squad statistics if available"""
        try:
            if os.path.exists(self.squad_stats_file):
                df = pd.read_csv(self.squad_stats_file)
                print(f" Loaded squad statistics: {len(df)} teams")
                return df
        except Exception as e:
            print(f" Could not load squad stats: {e}")
        return None
    
    def calculate_team_performance_score(self, team_name, df_players):
        """Calculate performance score from player data"""
        if df_players is None:
            return 0.75  # Default
        
        # Filter players by nationality
        team_players = df_players[df_players['nationality_name'] == team_name]
        
        if len(team_players) == 0:
            return 0.75  # Default if no players found
        
        # Get top 23 players (squad size)
        top_squad = team_players.nlargest(23, 'overall')
        
        # Calculate weighted average (starters weigh more)
        top_11 = top_squad.head(11)['overall'].mean()
        bench = top_squad.iloc[11:23]['overall'].mean() if len(top_squad) > 11 else top_11
        
        # Weighted score: 70% starters, 30% bench
        avg_rating = (top_11 * 0.7 + bench * 0.3)
        
        # Normalize to 0-1 scale (FIFA ratings are 0-100)
        normalized_score = avg_rating / 100
        
        return round(normalized_score, 3)
    
    def get_48_teams_data(self):
        """
        Load and integrate all data sources to create complete 48-team dataset
        """
        print("\n Loading FIFA 2026 World Cup data from scraped sources...")
        
        # Load data sources
        df_rankings = self.load_fifa_rankings()
        df_players = self.load_player_data()
        df_squad_stats = self.load_squad_statistics()
        
        teams_data = []
        
        for team_name, team_info in self.wc_2026_teams.items():
            team_dict = {
                'name': team_name,
                'confederation': team_info['confederation'],
                'status': team_info['status']
            }
            
            # Get FIFA ranking data
            if df_rankings is not None:
                team_row = df_rankings[df_rankings['team'] == team_name]
                
                if len(team_row) > 0:
                    team_dict['rank'] = int(team_row.iloc[0]['rank'])
                    team_dict['points'] = int(team_row.iloc[0]['total.points'])
                else:
                    # Fallback: estimate based on position in list
                    team_dict['rank'] = list(self.wc_2026_teams.keys()).index(team_name) + 1
                    team_dict['points'] = 1500
            
            # Calculate performance score from player data
            if df_players is not None:
                team_dict['score'] = self.calculate_team_performance_score(team_name, df_players)
            else:
                # Fallback: estimate from rank
                team_dict['score'] = max(0.65, 1.0 - (team_dict.get('rank', 25) * 0.01))
            
            # Add squad statistics if available
            if df_squad_stats is not None:
                squad_row = df_squad_stats[df_squad_stats['team_name'] == team_name]
                if len(squad_row) > 0:
                    team_dict['avg_overall'] = round(squad_row.iloc[0].get('avg_overall', 75), 1)
                    team_dict['max_overall'] = int(squad_row.iloc[0].get('max_overall', 85))
                    team_dict['squad_size'] = int(squad_row.iloc[0].get('squad_size', 23))
            
            teams_data.append(team_dict)
        
        # Sort alphabetically within each status group (Qualified first, then Projected)
        teams_data.sort(key=lambda x: (0 if x['status'] == 'Qualified' else 1, x['name']))
        
        print(f" Loaded {len(teams_data)} FIFA 2026 World Cup teams")
        print(f" Data sources:")
        print(f"   • FIFA Rankings: {'' if df_rankings is not None else ''}")
        print(f"   • Player Database: {'' if df_players is not None else ''} ({len(df_players)} players)" if df_players is not None else "   • Player Database: ")
        print(f"   • Squad Statistics: {'' if df_squad_stats is not None else ''}")
        
        return teams_data
    
    def get_player_stats_for_team(self, team_name, df_players=None, min_year=2022):
        """Get detailed player statistics for a specific team (FIFA 22 onwards by default)"""
        if df_players is None:
            df_players = self.load_player_data()
        
        if df_players is None:
            return None
        
        # Filter by year if fifa_version column exists
        # FIFA 22 = version 22 (2021/2022), FIFA 23 = version 23 (2022/2023), etc.
        # FIFA version N corresponds to year N-1 to year N
        if 'fifa_version' in df_players.columns and min_year:
            # Convert min_year to FIFA version (2022 -> version 22 or higher)
            min_version = min_year - 2000  # 2022 -> 22
            df_players = df_players[df_players['fifa_version'] >= min_version]
        
        team_players = df_players[df_players['nationality_name'] == team_name]
        
        if len(team_players) == 0:
            return None
        
        # Get top 23 players
        top_squad = team_players.nlargest(23, 'overall')
        
        # Prepare top players list with key info
        top_players_list = []
        if 'player_name' in top_squad.columns:
            for idx, player in top_squad.head(13).iterrows():  # Top 13 players
                player_info = {
                    'name': player.get('player_name', 'Unknown'),
                    'overall': int(player.get('overall', 0)),
                    'position': player.get('player_positions', 'N/A'),
                    'age': int(player.get('age', 0)) if pd.notna(player.get('age')) else None,
                    'club': player.get('club_name', 'N/A'),
                    'value': f"€{player.get('value_eur', 0)/1000000:.1f}M" if pd.notna(player.get('value_eur')) and player.get('value_eur', 0) > 0 else 'N/A'
                }
                top_players_list.append(player_info)
        
        stats = {
            'total_players': len(team_players),
            'squad_size': len(top_squad),
            'avg_overall': round(top_squad['overall'].mean(), 1),
            'max_overall': int(top_squad['overall'].max()),
            'min_overall': int(top_squad['overall'].min()),
            'avg_age': round(top_squad['age'].mean(), 1) if 'age' in top_squad.columns else None,
            'top_players': top_players_list,
            'data_year': f'FIFA {int(df_players["fifa_version"].mode()[0])}' if 'fifa_version' in df_players.columns else 'FIFA 26'
        }
        
        return stats

# Singleton instance
_data_loader = None

def get_data_loader(auto_scrape=True):
    """
    Get or create the data loader singleton
    
    Args:
        auto_scrape: If True, run web scraper on first initialization to get fresh data
    """
    global _data_loader
    if _data_loader is None:
        _data_loader = FIFA2026DataLoader(auto_scrape=auto_scrape)
    return _data_loader

if __name__ == "__main__":
    # Test the data loader
    loader = FIFA2026DataLoader()
    teams = loader.get_48_teams_data()
    
    print("\n Sample teams:")
    for team in teams[:5]:
        print(f"  {team['rank']}. {team['name']} - {team['points']} pts (Score: {team['score']})")
    
    # Test player stats
    print("\n Player stats for Argentina:")
    stats = loader.get_player_stats_for_team('Argentina')
    if stats:
        print(f"  Total players in database: {stats['total_players']}")
        print(f"  Top squad avg rating: {stats['avg_overall']}")
        print(f"  Best player rating: {stats['max_overall']}")
        if stats['top_players']:
            print(f"  Top 5 players:")
            for player in stats['top_players']:
                print(f"    • {player['player_name']} ({player['overall']}) - {player['player_positions']}")
