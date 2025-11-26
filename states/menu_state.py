"""
Menu State
Handles main menu logic and rendering.
"""
import pygame
from states.base_state import BaseState
from managers.menu_manager import MenuManager
from utils.helpers import stable_hover, get_active_hand_position
import config


class MenuState(BaseState):
    """Main menu state."""
    
    def __init__(self, screen, sound_manager, menu_manager=None):
        """
        Initialize menu state.
        
        Args:
            screen: Pygame screen surface
            sound_manager: Sound manager instance
            menu_manager: Optional menu manager (created if not provided)
        """
        super().__init__(screen, sound_manager)
        
        # Menu manager
        if menu_manager:
            self.menu_manager = menu_manager
        else:
            self.menu_manager = MenuManager(screen, config.IMAGES_DIR)
        
        self.menu_manager.sound_manager = sound_manager
        
        # State variables
        self.click_timer = 0.0
        self.prev_hand_pos = None
    
    def on_enter(self):
        """Start menu music when entering."""
        if self.sound_manager.current_music != 'menu':
            self.sound_manager.crossfade_music('menu', fade_out_ms=500, fade_in_ms=500)
        self.click_timer = 0.0
        self.prev_hand_pos = None
    
    def on_exit(self):
        """Cleanup when leaving menu."""
        self.click_timer = 0.0
    
    def update(self, dt, landmarks, hand_info):
        """
        Update menu logic.
        
        Args:
            dt: Delta time
            landmarks: Pose landmarks (not used in menu)
            hand_info: Hand detection info
        
        Returns:
            int or None: Next state ID or None to stay
        """
        active_hand_pos = get_active_hand_position(hand_info)
        hovered_button = self.menu_manager.check_button_hover(active_hand_pos)
        
        if hovered_button and stable_hover(active_hand_pos, self.prev_hand_pos, config.HOVER_STABILITY_THRESHOLD):
            self.click_timer += dt
            
            if self.click_timer >= config.CLICK_HOLD_TIME:
                self.menu_manager.play_button_sound()
                self.click_timer = 0.0
                
                # Return next state
                if hovered_button == "start":
                    return config.GAME_COUNTDOWN
                elif hovered_button == "credits":
                    return config.GAME_CREDITS
                elif hovered_button == "guide":
                    return config.GAME_GUIDE
        else:
            self.click_timer = 0.0
        
        self.prev_hand_pos = active_hand_pos
        return None
    
    def render(self):
        """Render menu screen."""
        self.menu_manager.draw_menu()
    
    def handle_event(self, event):
        """
        Handle keyboard events.
        
        Args:
            event: Pygame event
        
        Returns:
            int or None: Next state ID or None
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return config.GAME_COUNTDOWN
        return None
