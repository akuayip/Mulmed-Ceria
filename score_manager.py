"""
Score Manager Module
Manages game score, lives, and game state.
"""

import time


class ScoreManager:
    """
    Manages score, lives, game state, and power-ups.
    """

    def __init__(self, starting_lives=3):
        """
        Initialize ScoreManager.

        Args:
            starting_lives: Number of lives at game start
        """
        self.score = 0
        self.lives = starting_lives
        self.max_lives = starting_lives
        self.high_score = 0
        self.game_over = False
        self.game_won = False
        self.level = 1
        
        # Power-up states
        self.shield_active = False
        self.shield_duration = 0
        self.double_score_active = False
        self.double_score_duration = 0
        self.slow_motion_active = False
        self.slow_motion_duration = 0
        
        # Stats
        self.targets_hit = 0
        self.obstacles_dodged = 0
        self.start_time = time.time()

    def add_score(self, points: int):
        """
        Add points to score.

        Args:
            points: Points to add
        """
        multiplier = 2 if self.double_score_active else 1
        self.score += points * multiplier
        
        if self.score > self.high_score:
            self.high_score = self.score

    def subtract_score(self, points: int):
        """
        Subtract points from score.

        Args:
            points: Points to subtract
        """
        self.score = max(0, self.score - points)

    def lose_life(self, sound_manager):
        """Decrease lives by 1."""
        if self.shield_active:
            # Shield protects from damage
            return False
        
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
            sound_manager.play_sound('game_over')
        else:
            sound_manager.play_sound('damage')
        return True

    def add_life(self):
        """Add a life (max cap)."""
        self.lives = min(self.max_lives, self.lives + 1)

    def activate_powerup(self, powerup_type: str):
        """
        Activate a power-up.

        Args:
            powerup_type: Type of power-up ('shield', 'double_score', 'slow_motion')
        """
        if powerup_type == 'shield':
            self.shield_active = True
            self.shield_duration = 5.0
        elif powerup_type == 'double_score':
            self.double_score_active = True
            self.double_score_duration = 8.0
        elif powerup_type == 'slow_motion':
            self.slow_motion_active = True
            self.slow_motion_duration = 6.0

    def update(self, dt: float):
        """
        Update power-up durations.

        Args:
            dt: Delta time in seconds
        """
        # Update shield
        if self.shield_active:
            self.shield_duration -= dt
            if self.shield_duration <= 0:
                self.shield_active = False
                self.shield_duration = 0

        # Update double score
        if self.double_score_active:
            self.double_score_duration -= dt
            if self.double_score_duration <= 0:
                self.double_score_active = False
                self.double_score_duration = 0

        # Update slow motion
        if self.slow_motion_active:
            self.slow_motion_duration -= dt
            if self.slow_motion_duration <= 0:
                self.slow_motion_active = False
                self.slow_motion_duration = 0

    def reset(self):
        """Reset game state for new game."""
        self.score = 0
        self.lives = self.max_lives
        self.game_over = False
        self.game_won = False
        self.level = 1
        self.targets_hit = 0
        self.obstacles_dodged = 0
        self.shield_active = False
        self.double_score_active = False
        self.slow_motion_active = False
        self.start_time = time.time()

    def get_play_time(self) -> str:
        """
        Get formatted play time.

        Returns:
            str: Time in MM:SS format
        """
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        return f"{minutes:02d}:{seconds:02d}"

    def get_stats(self) -> dict:
        """
        Get game statistics.

        Returns:
            dict: Game stats
        """
        return {
            'score': self.score,
            'high_score': self.high_score,
            'lives': self.lives,
            'targets_hit': self.targets_hit,
            'obstacles_dodged': self.obstacles_dodged,
            'play_time': self.get_play_time(),
            'level': self.level
        }
