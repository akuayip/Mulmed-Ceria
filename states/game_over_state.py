"""
Game Over State
Handles game over screen and results.
"""
import pygame
from states.base_state import BaseState
from utils.helpers import stable_hover, get_active_hand_position
import config


class GameOverState(BaseState):
    """Game over state."""
    
    def __init__(self, screen, sound_manager, game_engine, game_renderer):
        """
        Initialize game over state.
        
        Args:
            screen: Pygame screen surface
            sound_manager: Sound manager instance
            game_engine: Game engine instance
            game_renderer: Game renderer instance
        """
        super().__init__(screen, sound_manager)
        self.game_engine = game_engine
        self.game_renderer = game_renderer
        
        # State variables
        self.game_over_timer = 0
        self.phase = 1  # 1 = intro (logo), 2 = results
        self.play_duration = 0
        self.click_timer = 0.0
        self.prev_hand_pos = None
    
    def on_enter(self):
        """Initialize game over state."""
        self.sound_manager.stop_music()
        self.sound_manager.play_sound('game_over')
        self.game_over_timer = 0
        self.phase = 1
        self.click_timer = 0.0
        self.prev_hand_pos = None
    
    def on_exit(self):
        """Cleanup when leaving game over."""
        self.game_over_timer = 0
        self.phase = 1
    
    def update(self, dt, landmarks, hand_info):
        """
        Update game over logic.
        
        Args:
            dt: Delta time
            landmarks: Pose landmarks (not used)
            hand_info: Hand detection info
        
        Returns:
            int or None: GAME_MENU if menu button clicked
        """
        self.game_over_timer += dt
        
        # Transition from phase 1 to phase 2
        if self.phase == 1 and self.game_over_timer >= config.GAME_OVER_INTRO_DURATION:
            self.phase = 2
        
        # Check for menu button click in phase 2
        if self.phase == 2:
            active_hand_pos = get_active_hand_position(hand_info)
            
            # Simple click detection for menu button (bottom left corner)
            if active_hand_pos:
                x, y = active_hand_pos
                # Menu button area: (30, screen_height - 130) to (110, screen_height - 50)
                if 30 <= x <= 110 and self.screen.get_height() - 130 <= y <= self.screen.get_height() - 50:
                    if stable_hover(active_hand_pos, self.prev_hand_pos, 50):
                        self.click_timer += dt
                        
                        if self.click_timer >= config.CLICK_HOLD_TIME:
                            self.sound_manager.play_sound('button')
                            return config.GAME_MENU
                else:
                    self.click_timer = 0.0
            
            self.prev_hand_pos = active_hand_pos
        
        return None
    
    def render(self):
        """Render game over screen."""
        self.game_renderer.draw_game_over_screen(
            self.game_engine.score_manager,
            self.play_duration,
            self.phase
        )
    
    def set_play_duration(self, duration):
        """
        Set the play duration to display.
        
        Args:
            duration: Play duration in seconds
        """
        self.play_duration = duration
    
    def handle_event(self, event):
        """
        Handle events.
        
        Args:
            event: Pygame event
        
        Returns:
            int or None: Next state or None
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                return config.GAME_COUNTDOWN
            elif event.key == pygame.K_ESCAPE:
                return config.GAME_MENU
        return None
