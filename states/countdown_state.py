"""
Countdown State
Handles countdown animation before gameplay.
"""
import pygame
from states.base_state import BaseState
import config


class CountdownState(BaseState):
    """Countdown state (3, 2, 1 before gameplay)."""
    
    def __init__(self, screen, sound_manager, game_renderer):
        """
        Initialize countdown state.
        
        Args:
            screen: Pygame screen surface
            sound_manager: Sound manager instance
            game_renderer: Game renderer instance
        """
        super().__init__(screen, sound_manager)
        self.game_renderer = game_renderer
        self.countdown_timer = config.COUNTDOWN_DURATION
    
    def on_enter(self):
        """Reset countdown and play sound."""
        self.countdown_timer = config.COUNTDOWN_DURATION
        self.sound_manager.stop_music()
        self.sound_manager.play_sound('countdown')
    
    def on_exit(self):
        """Cleanup when leaving countdown."""
        pass
    
    def update(self, dt, landmarks, hand_info):
        """
        Update countdown timer.
        
        Args:
            dt: Delta time
            landmarks: Pose landmarks (not used)
            hand_info: Hand detection info (not used)
        
        Returns:
            int or None: GAME_PLAY when countdown finishes
        """
        self.countdown_timer -= dt
        
        if self.countdown_timer <= 0:
            return config.GAME_PLAY
        
        return None
    
    def render(self):
        """Render countdown animation."""
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
    
    def handle_event(self, event):
        """
        Handle events.
        
        Args:
            event: Pygame event
        
        Returns:
            int or None: GAME_MENU if ESC pressed
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return config.GAME_MENU
        return None
