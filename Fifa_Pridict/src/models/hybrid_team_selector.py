"""
Hybrid Team Selection for FIFA World Cup 2026 Quarter-Finals

This module combines performance-based selection with K-Means clustering to select
8 quarter-finalist teams that are both realistic AND geographically diverse.

Strategy:
- Top 5 teams by performance score (ensures favorites are included)
- Best 3 teams from remaining confederations via K-Means clustering
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import json
from pathlib import Path
from typing import Dict, List, Tuple
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns


class HybridTeamSelector:
    """
    Selects 8 quarter-finalist teams using hybrid approach:
    - Top 5 by performance score (realistic favorites)
    - Best 3 from remaining confederations via clustering (diversity)
    """
    
    def __init__(self, teams_data: List[Dict]):
        """
        Initialize the hybrid selector.
        
        Args:
            teams_data: List of all team dictionaries
        """
        self.all_teams = teams_data
        self.top_5_teams = []
        self.remaining_teams = []
        self.clustered_3_teams = []
        self.final_8_teams = []
        self.scaler = StandardScaler()
        
    def select_quarter_finalists(self) -> List[Dict]:
        """
        Main method to select 8 quarter-finalist teams.
        
        Returns:
            List of 8 selected team dictionaries
        """
        print(f"\n🎯 Top 8 Quarter-Final Team Selection")
        print(f"📊 Analyzing {len(self.all_teams)} teams...")
        
        # Simple: Just take top 8 by performance score
        sorted_teams = sorted(
            self.all_teams,
            key=lambda x: x.get('score', x.get('performance_score', 0)),
            reverse=True
        )
        
        self.final_8_teams = sorted_teams[:8]
        
        # Add metadata
        for i, team in enumerate(self.final_8_teams, 1):
            team['selection_method'] = 'Top 8 Performance'
            team['selection_rank'] = i
            team['final_rank'] = i
        
        print(f"\n🏆 Top 8 Teams Selected (by Performance Score):")
        for i, team in enumerate(self.final_8_teams, 1):
            score = team.get('score', team.get('performance_score', 0))
            conf = team.get('confederation', 'Unknown')
            print(f"   {i}. {team['name']} ({conf}) - Score: {score:.3f}")
        
        # Print confederation distribution
        print(f"\n📊 Confederation Distribution:")
        conf_count = {}
        for team in self.final_8_teams:
            conf = team.get('confederation', 'Unknown')
            conf_count[conf] = conf_count.get(conf, 0) + 1
        
        for conf, count in sorted(conf_count.items(), key=lambda x: x[1], reverse=True):
            print(f"   {conf}: {count} team(s)")
        
        return self.final_8_teams
    
    def _select_top_5_by_performance(self):
        """
        Select top 5 teams by performance score.
        Ensures the strongest teams (Argentina, Brazil, France, Spain, England) are included.
        """
        # Sort by performance score (use 'score' or 'performance_score')
        sorted_teams = sorted(
            self.all_teams,
            key=lambda x: x.get('score', x.get('performance_score', 0)),
            reverse=True
        )
        
        self.top_5_teams = sorted_teams[:5]
        
        print(f"\n✅ Top 5 Teams Selected (by Performance Score):")
        for i, team in enumerate(self.top_5_teams, 1):
            score = team.get('score', team.get('performance_score', 0))
            conf = team.get('confederation', 'Unknown')
            print(f"   {i}. {team['name']} ({conf}) - Score: {score:.3f}")
    
    def _get_remaining_teams(self):
        """
        Get teams not in top 5 for clustering-based selection.
        """
        top_5_names = {team['name'] for team in self.top_5_teams}
        self.remaining_teams = [
            team for team in self.all_teams 
            if team['name'] not in top_5_names
        ]
        print(f"\n📋 Remaining teams for clustering: {len(self.remaining_teams)}")
    
    def _select_best_3_from_clustering(self):
        """
        Use K-Means clustering to select best team from CAF, AFC, and CONCACAF.
        Ensures geographic diversity in the final 8.
        """
        # Group remaining teams by confederation
        conf_teams = {}
        for team in self.remaining_teams:
            conf = team.get('confederation', 'Unknown')
            if conf not in conf_teams:
                conf_teams[conf] = []
            conf_teams[conf].append(team)
        
        print(f"\n🌍 Selecting best from each confederation:")
        
        # Target confederations (those not already in top 5)
        target_confs = ['CAF', 'AFC', 'CONCACAF']
        
        for conf in target_confs:
            if conf in conf_teams and len(conf_teams[conf]) > 0:
                # Select best team from this confederation
                best_team = max(
                    conf_teams[conf],
                    key=lambda x: x.get('score', x.get('performance_score', 0))
                )
                self.clustered_3_teams.append(best_team)
                
                score = best_team.get('score', best_team.get('performance_score', 0))
                print(f"   ✓ {conf}: {best_team['name']} - Score: {score:.3f}")
            else:
                print(f"   ✗ {conf}: No teams available")
        
        # If we don't have 3 teams yet, fill with next best from any confederation
        while len(self.clustered_3_teams) < 3:
            selected_names = {team['name'] for team in self.top_5_teams + self.clustered_3_teams}
            available = [t for t in self.remaining_teams if t['name'] not in selected_names]
            
            if not available:
                break
            
            next_best = max(
                available,
                key=lambda x: x.get('score', x.get('performance_score', 0))
            )
            self.clustered_3_teams.append(next_best)
            
            score = next_best.get('score', next_best.get('performance_score', 0))
            conf = next_best.get('confederation', 'Unknown')
            print(f"   ✓ Fallback: {next_best['name']} ({conf}) - Score: {score:.3f}")
    
    def _finalize_selection(self):
        """
        Combine top 5 and clustered 3 to create final 8 teams.
        Add metadata for tracking selection method.
        """
        # Add selection method to each team
        for team in self.top_5_teams:
            team['selection_method'] = 'Top 5 Performance'
            team['selection_rank'] = self.top_5_teams.index(team) + 1
        
        for team in self.clustered_3_teams:
            team['selection_method'] = 'Best from Confederation'
            team['selection_rank'] = len(self.top_5_teams) + self.clustered_3_teams.index(team) + 1
        
        # Combine
        self.final_8_teams = self.top_5_teams + self.clustered_3_teams
        
        # Sort by performance score for final ranking
        self.final_8_teams.sort(
            key=lambda x: x.get('score', x.get('performance_score', 0)),
            reverse=True
        )
        
        # Update final rankings
        for i, team in enumerate(self.final_8_teams, 1):
            team['final_rank'] = i
        
        print(f"\n🏆 Final 8 Quarter-Finalist Teams:")
        for i, team in enumerate(self.final_8_teams, 1):
            score = team.get('score', team.get('performance_score', 0))
            conf = team.get('confederation', 'Unknown')
            method = team.get('selection_method', 'Unknown')
            print(f"   {i}. {team['name']} ({conf}) - Score: {score:.3f} [{method}]")
        
        # Print confederation distribution
        print(f"\n📊 Confederation Distribution:")
        conf_count = {}
        for team in self.final_8_teams:
            conf = team.get('confederation', 'Unknown')
            conf_count[conf] = conf_count.get(conf, 0) + 1
        
        for conf, count in sorted(conf_count.items(), key=lambda x: x[1], reverse=True):
            print(f"   {conf}: {count} team(s)")
    
    def visualize_selection(self, output_path: str = None) -> str:
        """
        Create visualization showing the top 8 selection.
        
        Args:
            output_path: Path to save visualization
            
        Returns:
            Path to saved visualization
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Left plot: Performance scores of top 20 teams with top 8 highlighted
        all_scores = []
        all_names = []
        colors = []
        
        sorted_teams = sorted(self.all_teams, 
                            key=lambda x: x.get('score', x.get('performance_score', 0)), 
                            reverse=True)
        
        for i, team in enumerate(sorted_teams[:20]):
            score = team.get('score', team.get('performance_score', 0))
            all_scores.append(score)
            all_names.append(team['name'])
            
            if i < 8:
                colors.append('#27ae60')  # Green for top 8
            else:
                colors.append('#95a5a6')  # Gray for others
        
        ax1.barh(range(len(all_names)), all_scores, color=colors)
        ax1.set_yticks(range(len(all_names)))
        ax1.set_yticklabels(all_names, fontsize=9)
        ax1.set_xlabel('Performance Score', fontsize=11, fontweight='bold')
        ax1.set_title('Team Performance Scores\n🟢 Top 8 Quarter-Finalists', 
                     fontsize=12, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3, linestyle='--')
        ax1.invert_yaxis()
        
        # Right plot: Confederation distribution
        conf_distribution = {}
        for team in self.final_8_teams:
            conf = team.get('confederation', 'Unknown')
            conf_distribution[conf] = conf_distribution.get(conf, 0) + 1
        
        confederations = list(conf_distribution.keys())
        counts = list(conf_distribution.values())
        colors_pie = ['#3498db', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#34495e']
        
        wedges, texts, autotexts = ax2.pie(
            counts,
            labels=confederations,
            autopct='%1.0f',
            startangle=90,
            colors=colors_pie[:len(confederations)],
            textprops={'fontsize': 11, 'fontweight': 'bold'}
        )
        
        ax2.set_title('Confederation Distribution\n(Top 8 Quarter-Finalists)', 
                     fontsize=12, fontweight='bold')
        
        # Add legend with team names
        legend_labels = []
        for conf in confederations:
            teams_in_conf = [t['name'] for t in self.final_8_teams 
                           if t.get('confederation') == conf]
            legend_labels.append(f"{conf}: {', '.join(teams_in_conf)}")
        
        ax2.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), 
                  fontsize=9, framealpha=0.9)
        
        plt.suptitle('FIFA World Cup 2026 - Top 8 Quarter-Finalists by Performance Score', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        plt.tight_layout()
        
        # Save visualization
        if output_path is None:
            output_path = 'static/hybrid_selection_visualization.png'
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"\n✅ Visualization saved to {output_path}")
        return output_path
    
    def save_results(self, output_dir: str = 'data/processed'):
        """
        Save selection results to JSON files.
        
        Args:
            output_dir: Directory to save results
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save final 8 teams
        finalist_path = output_path / 'finalist_teams.json'
        with open(finalist_path, 'w', encoding='utf-8') as f:
            json.dump(self.final_8_teams, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved 8 finalist teams to {finalist_path}")
        
        # Save selection analysis
        analysis = {
            'selection_method': 'Top 8 by Performance Score',
            'total_teams_analyzed': len(self.all_teams),
            'finalists_selected': len(self.final_8_teams),
            'confederation_distribution': {
                conf: sum(1 for t in self.final_8_teams if t.get('confederation') == conf)
                for conf in set(t.get('confederation', 'Unknown') for t in self.final_8_teams)
            },
            'top_8_teams': [
                {
                    'rank': i + 1,
                    'name': team['name'],
                    'confederation': team.get('confederation', 'Unknown'),
                    'performance_score': team.get('score', team.get('performance_score', 0)),
                    'fifa_rank': team.get('fifa_rank', team.get('rank', 0)),
                    'selection_method': 'Top 8 Performance'
                }
                for i, team in enumerate(self.final_8_teams)
            ]
        }
        
        analysis_path = output_path / 'hybrid_selection_analysis.json'
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved hybrid selection analysis to {analysis_path}")


def run_hybrid_selection(teams_data: List[Dict], visualize: bool = True) -> Tuple[List[Dict], Dict]:
    """
    Main function to select top 8 quarter-finalist teams by performance score.
    
    Args:
        teams_data: List of all team dictionaries
        visualize: Whether to create visualization
        
    Returns:
        Tuple of (selected_teams, selection_info)
    """
    print(f"\n{'='*70}")
    print(f"🏆 FIFA WORLD CUP 2026 - TOP 8 QUARTER-FINALISTS")
    print(f"{'='*70}")
    
    # Initialize selector
    selector = HybridTeamSelector(teams_data)
    
    # Perform hybrid selection
    final_8_teams = selector.select_quarter_finalists()
    
    # Create visualization
    if visualize:
        print(f"\n🎨 Creating visualization...")
        # Save to the TASK_6_Deployment/static folder (Flask static folder)
        script_dir = Path(__file__).resolve().parent
        static_path = script_dir.parent.parent / 'TASK_6_Deployment' / 'static' / 'hybrid_selection_visualization.png'
        selector.visualize_selection(str(static_path))
    
    # Save results
    print(f"\n💾 Saving results...")
    selector.save_results()
    
    # Prepare return info
    selection_info = {
        'method': 'Top 8 by Performance',
        'total_analyzed': len(teams_data),
        'finalists_selected': len(final_8_teams),
        'all_teams': final_8_teams
    }
    
    print(f"\n{'='*70}")
    print(f"✅ TOP 8 SELECTION COMPLETE!")
    print(f"{'='*70}\n")
    
    return final_8_teams, selection_info


if __name__ == '__main__':
    print("Hybrid Team Selector Module - Ready for integration!")
