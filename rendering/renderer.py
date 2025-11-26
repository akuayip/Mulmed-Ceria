"""
Main Game Renderer
Integrates all rendering components.
"""
import pygame
import os
import config
from rendering.stickman_renderer import StickmanRenderer
from rendering.ui_renderer import UIRenderer
from rendering.countdown_renderer import CountdownRenderer


class GameRenderer:
    """Main renderer that coordinates all rendering components."""
    
    def __init__(self, screen, assets_dir=config.IMAGES_DIR):
        """
        Initialize game renderer.
        
        Args:
            screen: Pygame screen surface
            assets_dir: Directory containing image assets
        """
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
    
    def _load_backgrounds(self):
        """Load background images."""
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
    
    def update_screen_size(self, new_w, new_h):
        """
        Update screen dimensions when resized.
        
        Args:
            new_w: New width
            new_h: New height
        """
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
    
    def clear_screen(self):
        """Clear screen with gameplay background or black."""
        if self.play_bg:
            self.screen.blit(self.play_bg, (0, 0))
        else:
            self.screen.fill(config.BLACK)
    
    def draw_game_objects(self, targets, obstacles, powerups):
        """
        Draw all game objects.
        
        Args:
            targets: List of target objects
            obstacles: List of obstacle objects
            powerups: List of powerup objects
        """
        for target in targets:
            target.draw(self.screen)
        
        for obstacle in obstacles:
            obstacle.draw(self.screen)
        
        for powerup in powerups:
            powerup.draw(self.screen)
    
    def draw_stickman(self, landmarks, pose_detector):
        """
        Draw stickman from pose landmarks.
        
        Args:
            landmarks: MediaPipe pose landmarks
            pose_detector: PoseDetector instance
        """
        self.stickman_renderer.draw(landmarks, pose_detector)
    
    def draw_hand_indicators(self, hand_info):
        """
        Draw hand position indicators.
        
        Args:
            hand_info: Hand detection info dictionary
        """
        self.ui_renderer.draw_hand_indicators(hand_info)
    
    def draw_ui(self, score_manager, clock, hand_info):
        """
        Draw all UI elements.
        
        Args:
            score_manager: ScoreManager instance
            clock: Pygame clock object
            hand_info: Hand detection info dictionary
        """
        self.ui_renderer.draw_lives(score_manager.lives)
        self.ui_renderer.draw_score(score_manager.score)
        self.ui_renderer.draw_fps(clock)
        self.ui_renderer.draw_powerups(score_manager)
        self.ui_renderer.draw_hand_status(hand_info)
        self.ui_renderer.draw_instructions()
    
    def draw_countdown(self, countdown_number):
        """
        Draw countdown number.
        
        Args:
            countdown_number: Number to display (1, 2, or 3)
        """
        self.countdown_renderer.draw(countdown_number)
    
    def draw_game_over_screen(self, score_manager, play_duration=0, phase=1):
        """
        Draw game over screen.
        
        Args:
            score_manager: ScoreManager instance
            play_duration: Total play time in seconds
            phase: 1 for intro (logo), 2 for results
        """
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
