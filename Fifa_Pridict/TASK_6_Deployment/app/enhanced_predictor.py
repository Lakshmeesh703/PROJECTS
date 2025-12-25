"""
Lakshmeesh's Enhanced FIFA Match Predictor
Multi-factor comparison model for realistic predictions with goal prediction
"""

import math
from goal_predictor import GoalPredictor

class EnhancedPredictor:
    """
    Enhanced prediction model that analyzes multiple factors:
    - FIFA World Ranking difference
    - Performance Score comparison
    - FIFA Points difference
    - Confederation strength analysis
    - Team status (Qualified vs Projected)
    """
    
    # Confederation strength weights (based on historical World Cup performance)
    CONFEDERATION_STRENGTH = {
        'UEFA': 1.15,      # Europe - strongest historically
        'CONMEBOL': 1.12,  # South America - very strong
        'CAF': 0.95,       # Africa - competitive
        'AFC': 0.92,       # Asia - developing
        'CONCACAF': 0.90,  # North/Central America
        'OFC': 0.85        # Oceania - weakest
    }
    
    # Feature weights for final probability calculation
    WEIGHTS = {
        'rank_advantage': 0.20,         # Reduced from 0.25
        'score_advantage': 0.50,        # INCREASED from 0.35 (MOST IMPORTANT!)
        'points_advantage': 0.15,       # Reduced from 0.20
        'confederation_advantage': 0.10, # Reduced from 0.15
        'status_advantage': 0.05        # Keep minimal
    }
    
    @staticmethod
    def calculate_rank_advantage(team1, team2):
        """
        Better rank = lower number = advantage
        Returns normalized advantage score for team1 (-1 to 1)
        """
        rank_diff = team2['rank'] - team1['rank']  # Positive if team1 has better rank
        # Normalize using sigmoid-like function
        normalized = math.tanh(rank_diff / 10.0)
        return normalized
    
    @staticmethod
    def calculate_score_advantage(team1, team2):
        """
        Direct performance score comparison
        Returns normalized advantage score for team1 (-1 to 1)
        """
        score_diff = team1['score'] - team2['score']
        # Normalize (scores are around 0.6-0.95)
        normalized = math.tanh(score_diff / 0.1)
        return normalized
    
    @staticmethod
    def calculate_points_advantage(team1, team2):
        """
        FIFA points comparison
        Returns normalized advantage score for team1 (-1 to 1)
        """
        points_diff = team1['points'] - team2['points']
        # Normalize (points typically range 1500-1900)
        normalized = math.tanh(points_diff / 100.0)
        return normalized
    
    @staticmethod
    def calculate_confederation_advantage(team1, team2):
        """
        Confederation strength comparison
        Returns normalized advantage score for team1 (-1 to 1)
        """
        strength1 = EnhancedPredictor.CONFEDERATION_STRENGTH.get(team1['confederation'], 1.0)
        strength2 = EnhancedPredictor.CONFEDERATION_STRENGTH.get(team2['confederation'], 1.0)
        strength_diff = strength1 - strength2
        # Normalize (differences typically small, 0.05-0.3)
        normalized = math.tanh(strength_diff / 0.15)
        return normalized
    
    @staticmethod
    def calculate_status_advantage(team1, team2):
        """
        Qualified teams have slight advantage over Projected teams
        Returns advantage score for team1 (-1 to 1)
        """
        status_value = {'Qualified': 1, 'Projected': 0}
        value1 = status_value.get(team1['status'], 0)
        value2 = status_value.get(team2['status'], 0)
        return float(value1 - value2)  # -1, 0, or 1
    
    @staticmethod
    def calculate_win_probability(team1, team2):
        """
        Calculate win probability using weighted multi-factor analysis
        
        Returns:
            dict: {
                'team1_probability': float (0-100),
                'team2_probability': float (0-100),
                'winner': str (team name),
                'winner_probability': float,
                'factors': dict (breakdown of contributing factors),
                'confidence': str ('high', 'medium', 'low')
            }
        """
        # Calculate individual factor advantages
        rank_adv = EnhancedPredictor.calculate_rank_advantage(team1, team2)
        score_adv = EnhancedPredictor.calculate_score_advantage(team1, team2)
        points_adv = EnhancedPredictor.calculate_points_advantage(team1, team2)
        conf_adv = EnhancedPredictor.calculate_confederation_advantage(team1, team2)
        status_adv = EnhancedPredictor.calculate_status_advantage(team1, team2)
        
        # Weighted combination
        W = EnhancedPredictor.WEIGHTS
        combined_advantage = (
            W['rank_advantage'] * rank_adv +
            W['score_advantage'] * score_adv +
            W['points_advantage'] * points_adv +
            W['confederation_advantage'] * conf_adv +
            W['status_advantage'] * status_adv
        )
        
        # Convert combined advantage to probability using logistic function
        # This gives smooth probabilities between 30% and 70% for close matches
        # and more extreme values for mismatches
        base_prob = 1 / (1 + math.exp(-5 * combined_advantage))  # Sigmoid
        team1_prob = base_prob * 100
        team2_prob = 100 - team1_prob
        
        # Determine winner
        winner = team1 if team1_prob > team2_prob else team2
        winner_prob = max(team1_prob, team2_prob)
        
        # Calculate confidence based on probability margin
        prob_diff = abs(team1_prob - team2_prob)
        if prob_diff > 30:
            confidence = 'high'
        elif prob_diff > 15:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        # Build factor breakdown for UI display
        factors = {
            'rank_advantage': {
                'team1_value': team1['rank'],
                'team2_value': team2['rank'],
                'advantage': rank_adv,
                'weight': W['rank_advantage'],
                'contribution': W['rank_advantage'] * rank_adv
            },
            'score_advantage': {
                'team1_value': round(team1['score'] * 100, 1),
                'team2_value': round(team2['score'] * 100, 1),
                'advantage': score_adv,
                'weight': W['score_advantage'],
                'contribution': W['score_advantage'] * score_adv
            },
            'points_advantage': {
                'team1_value': team1['points'],
                'team2_value': team2['points'],
                'advantage': points_adv,
                'weight': W['points_advantage'],
                'contribution': W['points_advantage'] * points_adv
            },
            'confederation_advantage': {
                'team1_value': team1['confederation'],
                'team2_value': team2['confederation'],
                'advantage': conf_adv,
                'weight': W['confederation_advantage'],
                'contribution': W['confederation_advantage'] * conf_adv
            },
            'status_advantage': {
                'team1_value': team1['status'],
                'team2_value': team2['status'],
                'advantage': status_adv,
                'weight': W['status_advantage'],
                'contribution': W['status_advantage'] * status_adv
            }
        }
        
        return {
            'team1_probability': round(team1_prob, 1),
            'team2_probability': round(team2_prob, 1),
            'winner': winner['name'],
            'winner_probability': round(winner_prob, 1),
            'confidence': confidence,
            'factors': factors,
            'combined_advantage': round(combined_advantage, 3)
        }
    
    @staticmethod
    def calculate_win_probability_with_goals(team1, team2, match_type='group'):
        """
        Enhanced prediction with goal prediction included
        
        Args:
            team1: Dict with team statistics
            team2: Dict with team statistics
            match_type: 'group', 'round_16', 'quarter', 'semi', 'final'
            
        Returns:
            dict: Complete match prediction with goals
        """
        # Get win probability (existing method)
        win_prediction = EnhancedPredictor.calculate_win_probability(team1, team2)
        
        # Create goal predictor instance (Random Forest needs initialization)
        goal_predictor = GoalPredictor()
        
        # Get goal prediction with SMART ROUNDING based on win probability!
        # Pass win probabilities so goals align with predicted winner
        goal_prediction = goal_predictor.predict_match_score(
            team1, 
            team2, 
            match_type,
            team1_win_prob=win_prediction['team1_probability'],
            team2_win_prob=win_prediction['team2_probability']
        )
        
        # Get top scorelines
        top_scorelines = goal_predictor.predict_score_probabilities(team1, team2, match_type)
        
        # Get over/under probabilities
        over_under = goal_predictor.get_over_under_probability(team1, team2, 2.5, match_type)
        
        # Combine everything
        return {
            **win_prediction,  # Include all win probability data
            'goals': {
                'team1_goals': goal_prediction['team1_goals'],
                'team2_goals': goal_prediction['team2_goals'],
                'total_goals': goal_prediction['total_goals'],
                'scoreline': goal_prediction['scoreline'],
                'team1_xG': goal_prediction['team1_xG'],
                'team2_xG': goal_prediction['team2_xG'],
                'top_scorelines': top_scorelines,
                'over_under': over_under
            }
        }
    
    @staticmethod
    def get_factor_explanation(factors, team1_name, team2_name):
        """
        Generate human-readable explanation of prediction factors
        
        Returns:
            list: List of explanation strings
        """
        explanations = []
        
        # Rank explanation
        rank_contrib = factors['rank_advantage']['contribution']
        if abs(rank_contrib) > 0.05:
            better_team = team1_name if rank_contrib > 0 else team2_name
            rank1 = factors['rank_advantage']['team1_value']
            rank2 = factors['rank_advantage']['team2_value']
            explanations.append(
                f" Ranking: {better_team} has better FIFA ranking (#{rank1} vs #{rank2})"
            )
        
        # Score explanation
        score_contrib = factors['score_advantage']['contribution']
        if abs(score_contrib) > 0.05:
            better_team = team1_name if score_contrib > 0 else team2_name
            score1 = factors['score_advantage']['team1_value']
            score2 = factors['score_advantage']['team2_value']
            explanations.append(
                f" Performance: {better_team} has higher performance score ({score1}% vs {score2}%)"
            )
        
        # Points explanation
        points_contrib = factors['points_advantage']['contribution']
        if abs(points_contrib) > 0.03:
            better_team = team1_name if points_contrib > 0 else team2_name
            explanations.append(
                f" FIFA Points: {better_team} has accumulated more FIFA ranking points"
            )
        
        # Confederation explanation
        conf_contrib = factors['confederation_advantage']['contribution']
        if abs(conf_contrib) > 0.03:
            better_team = team1_name if conf_contrib > 0 else team2_name
            conf1 = factors['confederation_advantage']['team1_value']
            conf2 = factors['confederation_advantage']['team2_value']
            explanations.append(
                f" Confederation: {better_team} ({conf1}) from historically stronger confederation than {conf2}"
            )
        
        # Status explanation
        status_contrib = factors['status_advantage']['contribution']
        if abs(status_contrib) > 0.01:
            better_team = team1_name if status_contrib > 0 else team2_name
            explanations.append(
                f" Status: {better_team} already qualified (proven tournament team)"
            )
        
        if not explanations:
            explanations.append(" Very evenly matched teams - close prediction")
        
        return explanations
