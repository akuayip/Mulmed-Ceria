"""
"""Main renderer - coordinates all rendering components."""
import pygame
import os
from typing import Optional, List, Any
import config
from rendering.stickman_renderer import StickmanRenderer
from rendering.ui_renderer import UIRenderer
from rendering.countdown_renderer import CountdownRenderer


class GameRenderer:
    """Integrates all rendering: backgrounds, stickman, UI, countdown."""
    
    def __init__(self, screen: pygame.Surface, assets_dir: str = config.IMAGES_DIR) -> None:
        """Initialize renderer with screen and load backgrounds."""
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.assets_dir = assets_dir
        
        # Initialize sub-renderers
        self.stickman_renderer = StickmanRenderer(screen)
        self.ui_renderer = UIRenderer(screen, assets_dir)
        self.countdown_renderer = CountdownRenderer(screen, assets_dir)
        
        # Load backgrounds
        self._load_backgrounds()
    
    def _load_backgrounds(self) -> None:
        """Load and scale background images."""
        # Gameplay background
        self.play_bg = None
        play_bg_path = os.path.join(self.assets_dir, 'main_page.png')
        if os.path.exists(play_bg_path):
            self.play_bg = pygame.image.load(play_bg_path).convert()
            self.play_bg = pygame.transform.scale(self.play_bg, (self.screen_width, self.screen_height))
        else:
            print(f"[Warning] Gameplay background not found: {play_bg_path}")
        
        # Game over background
        self.game_over_bg = None
        game_over_path = os.path.join(self.assets_dir, 'landing_page.png')
        if os.path.exists(game_over_path):
            self.game_over_bg = pygame.image.load(game_over_path).convert()
            self.game_over_bg = pygame.transform.scale(self.game_over_bg, (self.screen_width, self.screen_height))
        else:
            print(f"[Warning] Game over background not found: {game_over_path}")
        
        # Game over logo
        self.game_over_image = None
        logo_path = os.path.join(self.assets_dir, 'game_over.png')
        if os.path.exists(logo_path):
            self.game_over_image = pygame.image.load(logo_path).convert_alpha()
        else:
            print(f"[Warning] Game over logo not found: {logo_path}")
    
    def update_screen_size(self, new_w: int, new_h: int) -> None:
        """Update screen dimensions and rescale backgrounds."""
        self.screen_width = new_w
        self.screen_height = new_h
        
        # Update sub-renderers
        self.stickman_renderer.update_screen_size(new_w, new_h)
        self.ui_renderer.update_screen_size(new_w, new_h)
        self.countdown_renderer.update_screen_size(new_w, new_h)
        
        # Rescale backgrounds
        if self.play_bg:
            play_bg_path = os.path.join(self.assets_dir, 'main_page.png')
            if os.path.exists(play_bg_path):
                self.play_bg = pygame.image.load(play_bg_path).convert()
                self.play_bg = pygame.transform.scale(self.play_bg, (new_w, new_h))
        
        if self.game_over_bg:
            game_over_path = os.path.join(self.assets_dir, 'landing_page.png')
            if os.path.exists(game_over_path):
                self.game_over_bg = pygame.image.load(game_over_path).convert()
                self.game_over_bg = pygame.transform.scale(self.game_over_bg, (new_w, new_h))
    
    def clear_screen(self) -> None:
        """Draw gameplay background or fill with black."""
        if self.play_bg:
            self.screen.blit(self.play_bg, (0, 0))
        else:
            self.screen.fill(config.BLACK)
    
    def draw_game_objects(self, targets: List[Any], obstacles: List[Any], powerups: List[Any]) -> None:
        """Draw all game objects (targets, obstacles, powerups)."""
        for target in targets:
            target.draw(self.screen)
        
        for obstacle in obstacles:
            obstacle.draw(self.screen)
        
        for powerup in powerups:
            powerup.draw(self.screen)
    
    def draw_stickman(self, landmarks: Any, pose_detector: Any) -> None:
        """Draw stickman from pose landmarks."""
        self.stickman_renderer.draw(landmarks, pose_detector)
    
    def draw_hand_indicators(self, hand_info: Dict[str, Any]) -> None:
        """Draw hand position indicators."""
        self.ui_renderer.draw_hand_indicators(hand_info)
    
    def draw_ui(self, score_manager: Any, clock: pygame.time.Clock, hand_info: Dict[str, Any]) -> None:
        """Draw all UI elements (lives, score, FPS, powerups, hand status)."""
        self.ui_renderer.draw_lives(score_manager.lives)
        self.ui_renderer.draw_score(score_manager.score)
        self.ui_renderer.draw_fps(clock)
        self.ui_renderer.draw_powerups(score_manager)
        self.ui_renderer.draw_hand_status(hand_info)
        self.ui_renderer.draw_instructions()
    
    def draw_countdown(self, countdown_number: int) -> None:
        """Draw countdown number (1, 2, or 3)."""
        self.countdown_renderer.draw(countdown_number)
    
    def draw_game_over_screen(self, score_manager: Any, play_duration: float = 0, phase: int = 1) -> None:
        """Draw game over screen (phase 1=logo, phase 2=results)."""
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        if phase == 1:
            # Phase 1: Black screen + Game Over logo
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.set_alpha(150)
            overlay.fill(config.BLACK)
            self.screen.blit(overlay, (0, 0))
            
            if self.game_over_image:
                img_width = int(self.screen_width * 0.5)
                img_height = int(self.screen_height * 0.4)
                scaled_img = pygame.transform.scale(self.game_over_image, (img_width, img_height))
                img_x = (self.screen_width - img_width) // 2
                img_y = (self.screen_height - img_height) // 2
                self.screen.blit(scaled_img, (img_x, img_y))
            else:
                # Fallback text
                font_large = pygame.font.Font(None, 48)
                text = font_large.render("GAME OVER", True, config.RED)
                text_rect = text.get_rect(center=(center_x, center_y))
                self.screen.blit(text, text_rect)
        
        elif phase == 2:
            # Phase 2: Results screen
            if self.game_over_bg:
                self.screen.blit(self.game_over_bg, (0, 0))
            else:
                self.screen.fill(config.BLACK)
            
            self.ui_renderer.draw_game_over_text(score_manager.score, play_duration)
            self.ui_renderer.draw_menu_button()
