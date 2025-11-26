"""Guide state - displays tutorial and game controls."""
import pygame
from typing import Optional, Dict, Any
from states.base_state import BaseState
from utils.helpers import stable_hover, get_active_hand_position
import config


class GuideState(BaseState):
    """Tutorial screen with game instructions and back button."""
    
    def __init__(self, screen: pygame.Surface, sound_manager, menu_manager) -> None:
        """Initialize guide with screen, sound, and menu manager."""
        super().__init__(screen, sound_manager)
        self.menu_manager = menu_manager
        self.click_timer: float = 0.0
        self.prev_hand_pos: Optional[tuple] = None
    
    def on_enter(self) -> None:
        """Reset timers and hand position."""
        self.click_timer = 0.0
        self.prev_hand_pos = None
    
    def on_exit(self) -> None:
        """Reset click timer."""
        self.click_timer = 0.0
    
    def update(self, dt: float, landmarks: Optional[Any], hand_info: Dict[str, Any]) -> Optional[int]:
        """Detect hand hover on back button, return to menu when clicked."""
        active_hand_pos = get_active_hand_position(hand_info)
        hovered_button = self.menu_manager.check_button_hover(active_hand_pos)
        
        if hovered_button == "back" and stable_hover(active_hand_pos, self.prev_hand_pos, config.HOVER_STABILITY_THRESHOLD):
            self.click_timer += dt
            
            if self.click_timer >= config.CLICK_HOLD_TIME:
                try:
                    self.menu_manager.play_button_sound()
                except Exception as e:
                    print(f"[Warning] Failed to play button sound: {e}")
                self.click_timer = 0.0
                return config.GAME_MENU
        else:
            self.click_timer = 0.0
        
        self.prev_hand_pos = active_hand_pos
        return None
    
    def render(self) -> None:
        """Draw guide screen."""
        self.menu_manager.draw_guide_screen()
    
    def handle_event(self, event: pygame.event.Event) -> Optional[int]:
        """Handle keyboard: ESC=return to menu."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return config.GAME_MENU
        return None
