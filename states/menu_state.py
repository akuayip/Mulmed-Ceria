"""
Menu State Module

This module contains the MenuState class which handles the main menu display,
navigation through hand gestures and keyboard input, and state transitions.
"""
import pygame
from typing import Optional, Dict, Any
from states.base_state import BaseState
from managers.menu_manager import MenuManager
from utils.helpers import stable_hover, get_active_hand_position
import config


class MenuState(BaseState):
    """
    Main menu state that displays and handles menu navigation.
    
    This class manages:
    - Menu rendering with title and menu items
    - Keyboard navigation (up/down arrows, enter, escape)
    - Background music playback
    - State transitions to gameplay, guide, and credits
    
    Attributes:
        menu_manager: Manages menu items and selection logic
    """
    
    def __init__(self, screen: pygame.Surface, sound_manager, menu_manager: MenuManager) -> None:
        """Initialize menu with screen, sound, and menu manager."""
        super().__init__(screen, sound_manager)
        
        # Menu manager
        if menu_manager:
            self.menu_manager: MenuManager = menu_manager
        else:
            self.menu_manager: MenuManager = MenuManager(screen, config.IMAGES_DIR)
        
        self.menu_manager.sound_manager = sound_manager
        
        # State variables for hand gesture detection
        self.click_timer: float = 0.0
        self.prev_hand_pos: Optional[tuple] = None
    
    def on_enter(self) -> None:
        """Start/crossfade menu music and reset timers."""
        try:
            if self.sound_manager.current_music != 'menu':
                self.sound_manager.crossfade_music('menu', fade_out_ms=500, fade_in_ms=500)
        except Exception as e:
            print(f"[Warning] Failed to start menu music: {e}")
        
        self.click_timer = 0.0
        self.prev_hand_pos = None
    
    def on_exit(self) -> None:
        """Reset click timer."""
        self.click_timer = 0.0
    
    def update(self, dt: float, landmarks: Optional[Any], hand_info: Dict[str, Any]) -> Optional[int]:
        """Detect hand hover on buttons, return next state when clicked."""
        active_hand_pos = get_active_hand_position(hand_info)
        hovered_button = self.menu_manager.check_button_hover(active_hand_pos)
        
        # If hovering over button with stable hand position
        if hovered_button and stable_hover(active_hand_pos, self.prev_hand_pos, config.HOVER_STABILITY_THRESHOLD):
            self.click_timer += dt
            
            # Trigger button click after holding for specified duration
            if self.click_timer >= config.CLICK_HOLD_TIME:
                try:
                    self.menu_manager.play_button_sound()
                except Exception as e:
                    print(f"[Warning] Failed to play button sound: {e}")
                
                self.click_timer = 0.0
                
                # Return next state based on button clicked
                if hovered_button == "start":
                    return config.GAME_COUNTDOWN
                elif hovered_button == "credits":
                    return config.GAME_CREDITS
                elif hovered_button == "guide":
                    return config.GAME_GUIDE
        else:
            # Reset timer if not hovering or hand moved
            self.click_timer = 0.0
        
        self.prev_hand_pos = active_hand_pos
        return None
    
    def render(self) -> None:
        """Draw menu screen."""
        self.menu_manager.draw_menu()
    
    def handle_event(self, event: pygame.event.Event) -> Optional[int]:
        """Handle keyboard: ENTER=start game."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return config.GAME_COUNTDOWN
        return None
