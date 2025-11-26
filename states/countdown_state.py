"""
Countdown State Module

This module contains the CountdownState class which handles the countdown animation
(3, 2, 1) before gameplay begins.
"""
import pygame
from typing import Optional, Dict, Any
from states.base_state import BaseState
import config


class CountdownState(BaseState):
    """
    Countdown state that displays 3-2-1 countdown before gameplay.
    
    This class manages:
    - Countdown timer logic (3 seconds total)
    - Visual countdown number rendering
    - Countdown sound effect playback
    - Automatic transition to gameplay when countdown finishes
    
    Attributes:
        game_renderer: Renderer instance for drawing countdown visuals
        countdown_timer: Remaining countdown time in seconds
    """
    
    def __init__(self, screen: pygame.Surface, sound_manager, game_renderer) -> None:
        """Initialize countdown with screen, sound, and renderer."""
        super().__init__(screen, sound_manager)
        self.game_renderer = game_renderer
        self.countdown_timer: float = config.COUNTDOWN_DURATION
    
    def on_enter(self) -> None:
        """Reset timer, stop music, play countdown sound."""
        self.countdown_timer = config.COUNTDOWN_DURATION
        
        try:
            self.sound_manager.stop_music()
            self.sound_manager.play_sound('countdown')
        except Exception as e:
            print(f"[Warning] Failed to play countdown sound: {e}")
    
    def on_exit(self) -> None:
        """Cleanup when leaving countdown."""
        pass
    
    def update(self, dt: float, landmarks: Optional[Any], hand_info: Dict[str, Any]) -> Optional[int]:
        """Decrease timer, return GAME_PLAY when finished."""
        self.countdown_timer -= dt
        
        if self.countdown_timer <= 0:
            return config.GAME_PLAY
        
        return None
    
    def render(self) -> None:
        """Draw background and countdown number (3, 2, or 1)."""
        # Draw background
        self.game_renderer.clear_screen()
        
        # Determine which number to show
        if self.countdown_timer > 2.0:
            current_number = 3
        elif self.countdown_timer > 1.0:
            current_number = 2
        else:
            current_number = 1
        
        # Draw countdown number
        self.game_renderer.draw_countdown(current_number)
    
    def handle_event(self, event: pygame.event.Event) -> Optional[int]:
        """Handle keyboard: ESC=cancel to menu."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return config.GAME_MENU
        return None
