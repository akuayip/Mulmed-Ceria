"""
Score Manager Module

This module contains the ScoreManager class which handles all score tracking,
lives management, level progression, and temporary power-up states.
"""
import time
from typing import Optional, Dict, Any


class ScoreManager:
    """
    Tracks score, lives, level progression, and temporary power-ups.
    
    This class manages:
    - Score tracking with double-score multiplier support
    - Lives system with shield protection
    - Automatic level progression every 500 points
    - Three power-up types: shield, double_score, slow_motion
    - Game statistics (targets hit, obstacles dodged, play time)
    
    Attributes:
        score: Current score
        lives: Remaining lives
        max_lives: Maximum lives allowed
        high_score: Highest score achieved
        game_over: Whether game has ended
        game_won: Whether player won the game
        level: Current difficulty level
        shield_active: Whether shield power-up is active
        shield_duration: Remaining shield duration in seconds
        double_score_active: Whether double score power-up is active
        double_score_duration: Remaining double score duration in seconds
        slow_motion_active: Whether slow motion power-up is active
        slow_motion_duration: Remaining slow motion duration in seconds
        targets_hit: Total targets successfully hit
        obstacles_dodged: Total obstacles successfully dodged
        start_time: Timestamp when game session started
    """

    def __init__(self, starting_lives: int = 3) -> None:
        """Initialize score manager with starting lives."""
        self.score: int = 0
        self.lives: int = starting_lives
        self.max_lives: int = starting_lives
        self.high_score: int = 0

        self.game_over: bool = False
        self.game_won: bool = False
        self.level: int = 1

        # Power-up states
        self.shield_active: bool = False
        self.shield_duration: float = 0.0
        self.double_score_active: bool = False
        self.double_score_duration: float = 0.0
        self.slow_motion_active: bool = False
        self.slow_motion_duration: float = 0.0

        # Stats
        self.targets_hit: int = 0
        self.obstacles_dodged: int = 0
        self.start_time: float = time.time()

    def add_score(self, points: int, sound_manager=None) -> None:
        """Add points (2x if double_score active), level up every 500 points."""
        multiplier = 2 if self.double_score_active else 1
        old_score = self.score

        self.score += points * multiplier

        # Level up check (every 500 points)
        if (old_score // 500) < (self.score // 500):
            self.level += 1
            if sound_manager:
                try:
                    sound_manager.play_sound('level_up')
                except Exception as e:
                    print(f"[Warning] Failed to play level up sound: {e}")

        if self.score > self.high_score:
            self.high_score = self.score

    def subtract_score(self, points: int) -> None:
        """Reduce score (minimum 0)."""
        self.score = max(0, self.score - points)

    def lose_life(self, sound_manager=None) -> bool:
        """Lose 1 life unless shield active, return True if damage applied."""
        if self.shield_active:
            return False

        self.lives -= 1

        if self.lives <= 0:
            self.game_over = True
            if sound_manager:
                try:
                    sound_manager.play_sound('game_over')
                except Exception as e:
                    print(f"[Warning] Failed to play game over sound: {e}")
        else:
            if sound_manager:
                try:
                    sound_manager.play_sound('damage')
                except Exception as e:
                    print(f"[Warning] Failed to play damage sound: {e}")

        return True

    def add_life(self) -> None:
        """Add 1 life (max limit applied)."""
        self.lives = min(self.max_lives, self.lives + 1)

    def activate_powerup(self, powerup_type: str) -> None:
        """Activate powerup: shield (5s), double_score (8s), slow_motion (6s)."""
        if powerup_type == 'shield':
            self.shield_active = True
            self.shield_duration = 5.0
        elif powerup_type == 'double_score':
            self.double_score_active = True
            self.double_score_duration = 8.0
        elif powerup_type == 'slow_motion':
            self.slow_motion_active = True
            self.slow_motion_duration = 6.0

    def update(self, dt: float) -> None:
        """Update powerup timers, deactivate when expired."""
        if self.shield_active:
            self.shield_duration -= dt
            if self.shield_duration <= 0:
                self.shield_active = False

        if self.double_score_active:
            self.double_score_duration -= dt
            if self.double_score_duration <= 0:
                self.double_score_active = False

        if self.slow_motion_active:
            self.slow_motion_duration -= dt
            if self.slow_motion_duration <= 0:
                self.slow_motion_active = False

    def reset(self) -> None:
        """Reset all stats and powerups to initial state."""
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
        """Return play time formatted as MM:SS."""
        elapsed = int(time.time() - self.start_time)
        return f"{elapsed // 60:02d}:{elapsed % 60:02d}"

    def get_stats(self) -> Dict[str, Any]:
        """Return dict with score, lives, targets hit, etc."""
        return {
            'score': self.score,
            'high_score': self.high_score,
            'lives': self.lives,
            'targets_hit': self.targets_hit,
            'obstacles_dodged': self.obstacles_dodged,
            'play_time': self.get_play_time(),
            'level': self.level
        }
