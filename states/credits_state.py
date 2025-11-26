"""
Credits State
Handles credits screen display.
"""
import pygame
from states.base_state import BaseState
from utils.helpers import stable_hover, get_active_hand_position
import config


class CreditsState(BaseState):
    """Credits screen state."""
    
    def __init__(self, screen, sound_manager, menu_manager):
        """
        Initialize credits state.
        
        Args:
            screen: Pygame screen surface
            sound_manager: Sound manager instance
            menu_manager: Menu manager instance
        """
        super().__init__(screen, sound_manager)
        self.menu_manager = menu_manager
        self.click_timer = 0.0
        self.prev_hand_pos = None
    
    def on_enter(self):
        """Setup credits screen."""
        self.click_timer = 0.0
        self.prev_hand_pos = None
    
    def on_exit(self):
        """Cleanup when leaving credits."""
        self.click_timer = 0.0
    
    def update(self, dt, landmarks, hand_info):
        """
        Update credits logic.
        
        Args:
            dt: Delta time
            landmarks: Pose landmarks (not used)
            hand_info: Hand detection info
        
        Returns:
            int or None: GAME_MENU if back button clicked
        """
        active_hand_pos = get_active_hand_position(hand_info)
        hovered_button = self.menu_manager.check_button_hover(active_hand_pos)
        
        if hovered_button == "back" and stable_hover(active_hand_pos, self.prev_hand_pos, config.HOVER_STABILITY_THRESHOLD):
            self.click_timer += dt
            
            if self.click_timer >= config.CLICK_HOLD_TIME:
                self.menu_manager.play_button_sound()
                self.click_timer = 0.0
                return config.GAME_MENU
        else:
            self.click_timer = 0.0
        
        self.prev_hand_pos = active_hand_pos
        return None
    
    def render(self):
        """Render credits screen."""
        self.menu_manager.draw_credits_screen()
    
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
