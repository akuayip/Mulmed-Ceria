"""Game over state - displays final score and statistics."""
import pygame
from typing import Optional, Dict, Any
from states.base_state import BaseState
from utils.helpers import stable_hover, get_active_hand_position
import config


class GameOverState(BaseState):
    """Game over screen with two phases: intro logo, then detailed results."""
    
    def __init__(self, screen: pygame.Surface, sound_manager, game_engine, game_renderer) -> None:
        """Initialize game over with screen, sound, engine, and renderer."""
        super().__init__(screen, sound_manager)
        self.game_engine = game_engine
        self.game_renderer = game_renderer
        
        # State variables
        self.game_over_timer: float = 0.0
        self.phase: int = 1  # 1 = intro (logo), 2 = results
        self.play_duration: float = 0.0
        self.click_timer: float = 0.0
        self.prev_hand_pos: Optional[tuple] = None
    
    def on_enter(self) -> None:
        """Stop music, play game over sound, reset timers."""
        try:
            self.sound_manager.stop_music()
            self.sound_manager.play_sound('game_over')
        except Exception as e:
            print(f"[Warning] Failed to play game over sound: {e}")
        
        self.game_over_timer = 0.0
        self.phase = 1
        self.click_timer = 0.0
        self.prev_hand_pos = None
    
    def on_exit(self) -> None:
        """Reset timers and phase."""
        self.game_over_timer = 0.0
        self.phase = 1
    
    def update(self, dt: float, landmarks: Optional[Any], hand_info: Dict[str, Any]) -> Optional[int]:
        """Transition phases, detect menu button click in phase 2."""
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
                            try:
                                self.sound_manager.play_sound('button')
                            except Exception as e:
                                print(f"[Warning] Failed to play button sound: {e}")
                            return config.GAME_MENU
                else:
                    self.click_timer = 0.0
            
            self.prev_hand_pos = active_hand_pos
        
        return None
    
    def render(self) -> None:
        """Draw game over screen (logo in phase 1, results in phase 2)."""
        self.game_renderer.draw_game_over_screen(
            self.game_engine.score_manager,
            self.play_duration,
            self.phase
        )
    
    def set_play_duration(self, duration: float) -> None:
        """Set gameplay duration to display on screen."""
        self.play_duration = duration
    
    def handle_event(self, event: pygame.event.Event) -> Optional[int]:
        """Handle keyboard events for restart/menu."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                return config.GAME_COUNTDOWN
            elif event.key == pygame.K_ESCAPE:
                return config.GAME_MENU
        return None
