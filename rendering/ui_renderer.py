"""
UI Renderer
Handles rendering of user interface elements.
"""
import pygame
import os
import config


class UIRenderer:
    """Renders UI elements like score, lives, FPS, hand status."""
    
    def __init__(self, screen, assets_dir=config.IMAGES_DIR):
        """
        Initialize UI renderer.
        
        Args:
            screen: Pygame screen surface
            assets_dir: Directory containing UI assets
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.assets_dir = assets_dir
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 20)
        
        # Load assets
        self._load_assets()
    
    def _load_assets(self):
        """Load UI assets."""
        # Load blood image for lives
        self.blood_image = None
        blood_path = os.path.join(self.assets_dir, 'blood.png')
        if os.path.exists(blood_path):
            self.blood_image = pygame.image.load(blood_path).convert_alpha()
            self.blood_image = pygame.transform.smoothscale(self.blood_image, config.BLOOD_ICON_SIZE)
        else:
            print(f"[Warning] Blood image not found: {blood_path}")
        
        # Load menu button
        self.menu_button = None
        menu_path = os.path.join(self.assets_dir, 'menu.png')
        if os.path.exists(menu_path):
            self.menu_button = pygame.image.load(menu_path).convert_alpha()
            self.menu_button = pygame.transform.smoothscale(self.menu_button, (80, 80))
        else:
            print(f"[Warning] Menu button not found: {menu_path}")
    
    def update_screen_size(self, width, height):
        """Update screen dimensions."""
        self.screen_width = width
        self.screen_height = height
    
    def draw_lives(self, lives):
        """
        Draw lives indicator (blood icons).
        
        Args:
            lives: Number of lives remaining
        """
        blood_size = config.BLOOD_ICON_SIZE[0]
        blood_spacing = 10
        blood_start_x = 20
        blood_start_y = 20
        
        for i in range(lives):
            x = blood_start_x + i * (blood_size + blood_spacing)
            y = blood_start_y
            
            if self.blood_image:
                self.screen.blit(self.blood_image, (x, y))
            else:
                # Fallback: red circles
                pygame.draw.circle(self.screen, config.RED, (x + blood_size//2, y + blood_size//2), blood_size//2)
    
    def draw_score(self, score):
        """
        Draw score in top right corner.
        
        Args:
            score: Current score
        """
        score_text = self.font_medium.render(f"SCORE: {score}", True, config.WHITE)
        score_x = self.screen_width - score_text.get_width() - 20
        self.screen.blit(score_text, (score_x, 20))
    
    def draw_fps(self, clock):
        """
        Draw FPS counter in bottom right corner.
        
        Args:
            clock: Pygame clock object
        """
        fps = int(clock.get_fps())
        fps_text = self.font_small.render(f"FPS: {fps}", True, config.GREEN)
        fps_x = self.screen_width - fps_text.get_width() - 20
        fps_y = self.screen_height - fps_text.get_height() - 20
        self.screen.blit(fps_text, (fps_x, fps_y))
    
    def draw_powerups(self, score_manager):
        """
        Draw active powerups below lives indicator.
        
        Args:
            score_manager: ScoreManager instance
        """
        blood_size = config.BLOOD_ICON_SIZE[0]
        y_offset = 20 + blood_size + 15
        
        if score_manager.shield_active:
            shield_text = self.font_small.render(
                f"SHIELD: {int(score_manager.shield_duration)}s", True, (0, 150, 255)
            )
            self.screen.blit(shield_text, (20, y_offset))
            y_offset += 30

        if score_manager.double_score_active:
            double_text = self.font_small.render(
                f"2X SCORE: {int(score_manager.double_score_duration)}s", True, (255, 255, 0)
            )
            self.screen.blit(double_text, (20, y_offset))
            y_offset += 30

        if score_manager.slow_motion_active:
            slow_text = self.font_small.render(
                f"SLOW-MO: {int(score_manager.slow_motion_duration)}s", True, config.GREEN)
            self.screen.blit(slow_text, (20, y_offset))
            y_offset += 30
    
    def draw_hand_status(self, hand_info):
        """
        Draw hand status indicators in bottom left corner.
        
        Args:
            hand_info: Hand detection info dictionary
        """
        hand_status_y = self.screen_height - 90
        
        # Title
        status_title = self.font_small.render("HAND STATUS:", True, config.WHITE)
        self.screen.blit(status_title, (20, hand_status_y))
        
        # Left hand status
        left_status = " FIST" if hand_info['left_hand']['is_fist'] else " OPEN"
        left_color = config.RED if hand_info['left_hand']['is_fist'] else config.CYAN
        left_detected = hand_info['left_hand']['position'] is not None
        
        if left_detected:
            left_text = self.font_small.render(f"LEFT: {left_status}", True, left_color)
        else:
            left_text = self.font_small.render("LEFT: ---", True, config.GRAY)
        self.screen.blit(left_text, (20, hand_status_y + 30))
        
        # Right hand status
        right_status = " FIST" if hand_info['right_hand']['is_fist'] else " OPEN"
        right_color = config.RED if hand_info['right_hand']['is_fist'] else config.CYAN
        right_detected = hand_info['right_hand']['position'] is not None
        
        if right_detected:
            right_text = self.font_small.render(f"RIGHT: {right_status}", True, right_color)
        else:
            right_text = self.font_small.render("RIGHT: ---", True, config.GRAY)
        self.screen.blit(right_text, (20, hand_status_y + 55))
    
    def draw_instructions(self):
        """Draw game instructions at bottom center."""
        inst_text = self.font_tiny.render(
            "PUNCH targets with FIST  | DODGE obstacles (red) | GRAB powerups (yellow)",
            True, config.WHITE
        )
        inst_x = self.screen_width // 2 - inst_text.get_width() // 2
        inst_y = self.screen_height - 25
        self.screen.blit(inst_text, (inst_x, inst_y))
    
    def draw_hand_indicators(self, hand_info):
        """
        Draw visual indicators around hands.
        
        Args:
            hand_info: Hand detection info dictionary
        """
        # Draw left hand indicator
        if hand_info['left_hand']['position']:
            pos = hand_info['left_hand']['position']
            is_fist = hand_info['left_hand']['is_fist']
            
            color = config.RED if is_fist else config.CYAN
            pygame.draw.circle(self.screen, color, pos, 35, 3)
            
            if is_fist:
                pygame.draw.circle(self.screen, config.RED, pos, 20)
                fist_text = self.font_tiny.render("FIST", True, config.RED)
                self.screen.blit(fist_text, (pos[0] - 20, pos[1] - 50))
        
        # Draw right hand indicator
        if hand_info['right_hand']['position']:
            pos = hand_info['right_hand']['position']
            is_fist = hand_info['right_hand']['is_fist']
            
            color = config.RED if is_fist else config.CYAN
            pygame.draw.circle(self.screen, color, pos, 35, 3)
            
            if is_fist:
                pygame.draw.circle(self.screen, config.RED, pos, 20)
                fist_text = self.font_tiny.render("FIST", True, config.RED)
                self.screen.blit(fist_text, (pos[0] - 20, pos[1] - 50))
    
    def draw_menu_button(self):
        """Draw menu button in bottom left corner."""
        if self.menu_button:
            self.screen.blit(self.menu_button, (30, self.screen_height - 130))
    
    def draw_game_over_text(self, score, play_duration):
        """
        Draw game over text with score and time.
        
        Args:
            score: Final score
            play_duration: Total play time in seconds
        """
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        # Calculate time (Minutes:Seconds)
        minutes = int(play_duration) // 60
        seconds = int(play_duration) % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        # Display score and time
        score_text = self.font_medium.render(f"FINAL SCORE: {score}", True, config.WHITE)
        time_text = self.font_medium.render(f"TIME PLAYED: {time_str}", True, (255, 255, 0))
        
        score_rect = score_text.get_rect(center=(center_x, center_y + 35))
        time_rect = time_text.get_rect(center=(center_x, center_y + 75))
        
        self.screen.blit(score_text, score_rect)
        self.screen.blit(time_text, time_rect)
