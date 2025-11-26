"""
Gameplay State
Handles main gameplay logic.
"""
import pygame
import time
from states.base_state import BaseState
import config


class GameplayState(BaseState):
    """Main gameplay state."""
    
    def __init__(self, screen, sound_manager, game_engine, game_renderer):
        """
        Initialize gameplay state.
        
        Args:
            screen: Pygame screen surface
            sound_manager: Sound manager instance
            game_engine: Game engine instance
            game_renderer: Game renderer instance
        """
        super().__init__(screen, sound_manager)
        self.game_engine = game_engine
        self.game_renderer = game_renderer
        self.start_time = 0
    
    def on_enter(self):
        """Start gameplay music and reset game."""
        self.sound_manager.play_music('gameplay', loops=-1, fade_ms=500)
        self.game_engine.reset_game()
        self.start_time = time.time()
    
    def on_exit(self):
        """Cleanup when leaving gameplay."""
        pass
    
    def update(self, dt, landmarks, hand_info):
        """
        Update gameplay logic.
        
        Args:
            dt: Delta time
            landmarks: Pose landmarks
            hand_info: Hand detection info
        
        Returns:
            int or None: GAME_OVER if game over, None otherwise
        """
        # Update game engine
        self.game_engine.update(dt, landmarks, hand_info)
        
        # Check game over
        if self.game_engine.score_manager.game_over:
            return config.GAME_OVER
        
        return None
    
    def render(self):
        """Render gameplay."""
        # Clear screen (draws background)
        self.game_renderer.clear_screen()
        
        # Draw game objects
        self.game_renderer.draw_game_objects(
            self.game_engine.targets,
            self.game_engine.obstacles,
            self.game_engine.powerups
        )
        
        # Draw stickman
        # Note: landmarks are not available here, will be passed through render_with_landmarks
        
    def render_with_landmarks(self, landmarks, hand_info, clock):
        """
        Render gameplay with landmarks and UI.
        
        Args:
            landmarks: Pose landmarks
            hand_info: Hand detection info
            clock: Pygame clock for FPS
        """
        # Draw stickman
        if landmarks:
            self.game_renderer.draw_stickman(landmarks, self.game_engine.pose_detector)
        
        # Draw hand indicators
        self.game_renderer.draw_hand_indicators(hand_info)
        
        # Draw UI
        self.game_renderer.draw_ui(self.game_engine.score_manager, clock, hand_info)
    
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
    
    def get_play_duration(self):
        """Get current play duration in seconds."""
        return time.time() - self.start_time
