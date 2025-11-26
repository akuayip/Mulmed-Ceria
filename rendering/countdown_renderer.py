"""
Countdown Renderer
Handles countdown animation rendering.
"""
import pygame
import os
import config


class CountdownRenderer:
    """Renders countdown animation."""
    
    def __init__(self, screen, assets_dir=config.IMAGES_DIR):
        """
        Initialize countdown renderer.
        
        Args:
            screen: Pygame screen surface
            assets_dir: Directory containing countdown images
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.assets_dir = assets_dir
        
        # Fonts (fallback if images not found)
        self.font_countdown = pygame.font.Font(None, 200)
        
        # Load countdown images
        self.countdown_images = {}
        self._load_countdown_images()
    
    def _load_countdown_images(self):
        """Load countdown number images."""
        for i in [1, 2, 3]:
            img_path = os.path.join(self.assets_dir, f'number_{i}.png')
            if os.path.exists(img_path):
                img = pygame.image.load(img_path).convert_alpha()
                self.countdown_images[i] = pygame.transform.smoothscale(img, config.COUNTDOWN_IMAGE_SIZE)
            else:
                print(f"[Warning] Countdown image not found: {img_path}")
    
    def update_screen_size(self, width, height):
        """Update screen dimensions."""
        self.screen_width = width
        self.screen_height = height
    
    def draw(self, countdown_number):
        """
        Draw countdown number.
        
        Args:
            countdown_number: Number to display (1, 2, or 3)
        """
        # Draw dark overlay
        dark_overlay = pygame.Surface((self.screen_width, self.screen_height))
        dark_overlay.set_alpha(180)
        dark_overlay.fill(config.BLACK)
        self.screen.blit(dark_overlay, (0, 0))
        
        # Draw countdown number
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        if countdown_number in self.countdown_images:
            # Use image if available
            img = self.countdown_images[countdown_number]
            img_rect = img.get_rect(center=(center_x, center_y))
            self.screen.blit(img, img_rect)
        else:
            # Fallback: draw text
            text = self.font_countdown.render(str(countdown_number), True, config.WHITE)
            text_rect = text.get_rect(center=(center_x, center_y))
            self.screen.blit(text, text_rect)
