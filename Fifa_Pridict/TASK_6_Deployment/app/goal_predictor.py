"""
Goal Prediction System for FIFA 2026 World Cup
Uses Random Forest Regression + Machine Learning methodology
"""

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle
import os

class GoalPredictor:
    """
    Advanced goal prediction using Random Forest Regression
    Trained on team statistics to predict realistic goal outcomes
    """
    
    # Historical average goals per match in World Cup
    WC_AVG_GOALS = 2.64  # FIFA World Cup historical average
    
    # Match type multipliers
    MATCH_MULTIPLIERS = {
        'group': 1.0,
        'round_16': 0.92,
        'quarter': 0.88,
        'semi': 0.85,
        'final': 0.82
    }
    
    def __init__(self):
        """Initialize the goal predictor with trained models"""
        self.team1_goals_model = None
        self.team2_goals_model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Try to load pre-trained models
        self._load_models()
        
        # If models don't exist, train them
        if not self.is_trained:
            self._train_models()
    
    def _load_models(self):
        """Load pre-trained models if they exist"""
        model_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'TASK_3_Model_Building', 'models')
        team1_model_path = os.path.join(model_dir, 'goal_prediction_team1.pkl')
        team2_model_path = os.path.join(model_dir, 'goal_prediction_team2.pkl')
        scaler_path = os.path.join(model_dir, 'goal_prediction_scaler.pkl')
        
        try:
            if os.path.exists(team1_model_path) and os.path.exists(team2_model_path):
                with open(team1_model_path, 'rb') as f:
                    self.team1_goals_model = pickle.load(f)
                with open(team2_model_path, 'rb') as f:
                    self.team2_goals_model = pickle.load(f)
                if os.path.exists(scaler_path):
                    with open(scaler_path, 'rb') as f:
                        self.scaler = pickle.load(f)
                self.is_trained = True
                print(" Loaded pre-trained goal prediction models")
        except Exception as e:
            print(f" Could not load models: {e}")
            self.is_trained = False
    
    def _train_models(self):
        """
        Train Random Forest models on synthetic data based on team statistics
        In production, this would use historical match results
        """
        print(" Training goal prediction models...")
        
        # Generate synthetic training data based on realistic patterns
        # Features: [attack_performance, defense_performance, performance_diff, avg_overall, rank_advantage]
        np.random.seed(42)
        n_samples = 1000
        
        # Simulate realistic team performance scores (0.5 to 0.95 like real teams)
        attack_performances = np.random.uniform(0.5, 0.95, n_samples)
        defense_performances = np.random.uniform(0.5, 0.95, n_samples)
        
        # Calculate performance differences (KEY for alignment with win probability!)
        performance_diffs = (attack_performances - defense_performances) * 100
        
        # Other features
        avg_overalls = np.random.uniform(60, 85, n_samples)
        rank_advantages = np.random.uniform(-50, 50, n_samples)
        
        X = np.column_stack([
            attack_performances * 100,  # 50-95 scale
            defense_performances * 100,  # 50-95 scale
            performance_diffs,           # -45 to +45 scale
            avg_overalls,                # 60-85 scale
            rank_advantages              # -50 to +50 scale
        ])
        
        # Generate target goals ALIGNED WITH PERFORMANCE SCORES
        # Higher performance score = more goals (matches win probability logic!)
        y_team1 = []
        y_team2 = []
        
        for i in range(n_samples):
            attack_perf = attack_performances[i]
            defense_perf = defense_performances[i]
            perf_diff = performance_diffs[i]
            
            # Base expected goals from performance scores
            # 0.5 performance -> 1.25 goals, 0.95 performance -> 2.375 goals
            base_attack_goals = attack_perf * 2.5
            base_defense_goals = defense_perf * 2.5
            
            # Adjust based on performance difference (same logic as win probability!)
            if perf_diff > 20:  # Strong attacker vs weak defender
                team1_expected = base_attack_goals * 1.4  # Boost attacker
                team2_expected = base_defense_goals * 0.6  # Reduce defender
            elif perf_diff < -20:  # Weak attacker vs strong defender
                team1_expected = base_attack_goals * 0.6  # Reduce attacker
                team2_expected = base_defense_goals * 1.4  # Boost defender
            else:  # Evenly matched
                team1_expected = base_attack_goals
                team2_expected = base_defense_goals
            
            # Add randomness but keep realistic (0-5 goals)
            team1_goals = np.clip(team1_expected + np.random.normal(0, 0.6), 0, 5)
            team2_goals = np.clip(team2_expected + np.random.normal(0, 0.6), 0, 5)
            
            y_team1.append(team1_goals)
            y_team2.append(team2_goals)
        
        y_team1 = np.array(y_team1)
        y_team2 = np.array(y_team2)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train models
        self.team1_goals_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42
        )
        self.team2_goals_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42
        )
        
        self.team1_goals_model.fit(X_scaled, y_team1)
        self.team2_goals_model.fit(X_scaled, y_team2)
        
        self.is_trained = True
        print(" Goal prediction models trained successfully")
        
        # Save models
        self._save_models()
    
    def _save_models(self):
        """Save trained models to disk"""
        try:
            model_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'TASK_3_Model_Building', 'models')
            os.makedirs(model_dir, exist_ok=True)
            
            with open(os.path.join(model_dir, 'goal_prediction_team1.pkl'), 'wb') as f:
                pickle.dump(self.team1_goals_model, f)
            with open(os.path.join(model_dir, 'goal_prediction_team2.pkl'), 'wb') as f:
                pickle.dump(self.team2_goals_model, f)
            with open(os.path.join(model_dir, 'goal_prediction_scaler.pkl'), 'wb') as f:
                pickle.dump(self.scaler, f)
            print(" Goal prediction models saved")
        except Exception as e:
            print(f" Could not save models: {e}")
    
    def _extract_features(self, attacking_team, defending_team):
        """
        Extract features for the regression model
        
        Returns:
            numpy array: Feature vector
        """
        # Use performance SCORE as primary factor (this determines win probability!)
        attack_performance_score = attacking_team.get('score', 0.75)  # 0-1 scale
        defense_performance_score = defending_team.get('score', 0.75)  # 0-1 scale
        
        # Scale performance scores to goal-relevant range
        # Higher performance score = more goals
        attack_strength = attack_performance_score * 100  # 0-100 scale
        
        # Defense strength (higher score = better defense = fewer goals conceded)
        defense_strength = defense_performance_score * 100  # 0-100 scale
        
        # Additional factors
        avg_overall_attack = attacking_team.get('avg_overall', 70)
        avg_overall_defense = defending_team.get('avg_overall', 70)
        
        # Rank difference (negative if attacking team has better rank = lower number)
        rank_attack = attacking_team.get('rank', 50)
        rank_defense = defending_team.get('rank', 50)
        rank_advantage = rank_defense - rank_attack  # Positive if attacker has better rank
        
        # Performance score difference (most important!)
        performance_advantage = (attack_performance_score - defense_performance_score) * 100
        
        # Return feature vector: [attack_performance, defense_performance, performance_diff, avg_overall, rank_advantage]
        return np.array([[
            attack_strength,           # Attacking team's performance score (0-100)
            defense_strength,          # Defending team's performance score (0-100)
            performance_advantage,     # Performance difference (-100 to +100)
            avg_overall_attack,        # Squad quality
            rank_advantage             # Rank advantage
        ]])
    
    def predict_match_score(self, team1, team2, match_type='group', team1_win_prob=None, team2_win_prob=None):
        """
        Predict match score between two teams using Random Forest Regression
        
        Args:
            team1: Dict with team statistics
            team2: Dict with team statistics  
            match_type: 'group', 'round_16', 'quarter', 'semi', 'final'
            team1_win_prob: Optional win probability for team1 (0-100)
            team2_win_prob: Optional win probability for team2 (0-100)
            
        Returns:
            dict: {
                'team1_goals': int,
                'team2_goals': int,
                'total_goals': int,
                'team1_xG': float,
                'team2_xG': float,
                'scoreline': str,
                'goal_breakdown': dict
            }
        """
        if not self.is_trained:
            self._train_models()
        
        # Extract features for both teams AS ATTACKERS
        team1_attacking_features = self._extract_features(team1, team2)
        team2_attacking_features = self._extract_features(team2, team1)
        
        # Scale features
        team1_features_scaled = self.scaler.transform(team1_attacking_features)
        team2_features_scaled = self.scaler.transform(team2_attacking_features)
        
        # Predict goals using Random Forest
        # Use team1_goals_model for BOTH (since features are from attacker's perspective)
        team1_xG_raw = self.team1_goals_model.predict(team1_features_scaled)[0]
        team2_xG_raw = self.team1_goals_model.predict(team2_features_scaled)[0]  # Use same model!
        
        # Apply match type multiplier
        multiplier = self.MATCH_MULTIPLIERS.get(match_type, 1.0)
        team1_xG = max(0.1, min(5.0, team1_xG_raw * multiplier))
        team2_xG = max(0.1, min(5.0, team2_xG_raw * multiplier))
        
        # SMART ROUNDING based on win probability!
        # Winner (higher win prob) → Round UP (ceiling)
        # Loser (lower win prob) → Round DOWN (floor)
        if team1_win_prob is not None and team2_win_prob is not None:
            if team1_win_prob > team2_win_prob:
                # Team1 is winning → round UP, Team2 losing → round DOWN
                team1_goals = int(np.ceil(team1_xG))
                team2_goals = int(np.floor(team2_xG))
            elif team2_win_prob > team1_win_prob:
                # Team2 is winning → round UP, Team1 losing → round DOWN
                team1_goals = int(np.floor(team1_xG))
                team2_goals = int(np.ceil(team2_xG))
            else:
                # Equal probability → normal rounding
                team1_goals = int(round(team1_xG))
                team2_goals = int(round(team2_xG))
        else:
            # No win probability provided → normal rounding
            team1_goals = int(round(team1_xG))
            team2_goals = int(round(team2_xG))
        
        # Ensure at least 0 goals
        team1_goals = max(0, team1_goals)
        team2_goals = max(0, team2_goals)
        
        # Calculate alternative scoreline probabilities (simulation-based)
        scoreline_probs = self._simulate_scoreline_probabilities(team1_xG, team2_xG)
        
        return {
            'team1_goals': team1_goals,
            'team2_goals': team2_goals,
            'total_goals': team1_goals + team2_goals,
            'team1_xG': round(team1_xG, 2),
            'team2_xG': round(team2_xG, 2),
            'scoreline': f"{team1_goals}-{team2_goals}",
            'goal_breakdown': {
                'team1_probabilities': {},
                'team2_probabilities': {}
            }
        }
    
    def _simulate_scoreline_probabilities(self, team1_xG, team2_xG, n_simulations=1000):
        """
        Simulate match outcomes to get scoreline probabilities
        """
        np.random.seed(None)  # Random seed for variety
        
        scorelines = {}
        for _ in range(n_simulations):
            # Add randomness around xG predictions
            g1 = max(0, int(round(np.random.normal(team1_xG, 0.8))))
            g2 = max(0, int(round(np.random.normal(team2_xG, 0.8))))
            
            # Cap at realistic maximum
            g1 = min(g1, 5)
            g2 = min(g2, 5)
            
            score = f"{g1}-{g2}"
            scorelines[score] = scorelines.get(score, 0) + 1
        
        # Convert counts to probabilities
        total = sum(scorelines.values())
        return {k: (v / total) * 100 for k, v in scorelines.items()}
    
    def predict_score_probabilities(self, team1, team2, match_type='group'):
        """
        Calculate probabilities for different scorelines using simulation
        
        Returns:
            list: Top 5 most likely scorelines with probabilities
        """
        # Get xG predictions
        prediction = self.predict_match_score(team1, team2, match_type)
        team1_xG = prediction['team1_xG']
        team2_xG = prediction['team2_xG']
        
        # Simulate scorelines
        scoreline_probs = self._simulate_scoreline_probabilities(team1_xG, team2_xG, n_simulations=2000)
        
        # Sort by probability
        sorted_scorelines = sorted(
            [{'score': k, 'probability': round(v, 2)} for k, v in scoreline_probs.items()],
            key=lambda x: x['probability'],
            reverse=True
        )
        
        return sorted_scorelines[:5]
    
    def get_over_under_probability(self, team1, team2, threshold=2.5, match_type='group'):
        """
        Calculate probability of over/under total goals using simulation
        
        Args:
            threshold: Goal threshold (e.g., 2.5 means over 2.5 or under 2.5)
            
        Returns:
            dict: {'over': float, 'under': float}
        """
        # Get xG predictions
        prediction = self.predict_match_score(team1, team2, match_type)
        total_xG = prediction['team1_xG'] + prediction['team2_xG']
        
        # Simulate total goals
        np.random.seed(None)
        simulations = 2000
        over_count = 0
        
        for _ in range(simulations):
            g1 = max(0, int(round(np.random.normal(prediction['team1_xG'], 0.8))))
            g2 = max(0, int(round(np.random.normal(prediction['team2_xG'], 0.8))))
            total = min(g1 + g2, 10)  # Cap at 10
            
            if total > threshold:
                over_count += 1
        
        over_prob = (over_count / simulations) * 100
        under_prob = 100 - over_prob
        
        return {
            'over': round(over_prob, 1),
            'under': round(under_prob, 1),
            'threshold': threshold,
            'expected_total': round(total_xG, 2)
        }


if __name__ == "__main__":
    # Test the goal predictor
    print("🎯 Goal Prediction System Test (Random Forest Regression)\n")
    
    # Create predictor instance
    predictor = GoalPredictor()
    
    # Example teams
    argentina = {
        'name': 'Argentina',
        'score': 0.85,
        'avg_overall': 67.8,
        'rank': 1
    }
    
    spain = {
        'name': 'Spain',
        'score': 0.856,
        'avg_overall': 69.15,
        'rank': 3
    }
    
    # Predict match
    prediction = predictor.predict_match_score(argentina, spain, 'final')
    
    print(f"Match: {argentina['name']} vs {spain['name']}")
    print(f"Predicted Score: {prediction['scoreline']}")
    print(f"Total Goals: {prediction['total_goals']}")
    print(f"\nExpected Goals (xG):")
    print(f"  {argentina['name']}: {prediction['team1_xG']}")
    print(f"  {spain['name']}: {prediction['team2_xG']}")
    
    # Top scorelines
    print(f"\nTop 5 Most Likely Scorelines:")
    scorelines = predictor.predict_score_probabilities(argentina, spain, 'final')
    for i, score in enumerate(scorelines, 1):
        print(f"  {i}. {score['score']} ({score['probability']}%)")
    
    # Over/Under
    over_under = predictor.get_over_under_probability(argentina, spain, 2.5, 'final')
    print(f"\nOver/Under 2.5 Goals:")
    print(f"  Over: {over_under['over']}%")
    print(f"  Under: {over_under['under']}%")
    print(f"  Expected Total: {over_under['expected_total']} goals")
    
    print("\n✅ Random Forest Goal Prediction System Ready!\n")
