"""
Menu Manager Module
Handles menu system, credits, and guide screens.
"""
import pygame
import os


class MenuManager:
    """Manages main menu, credits, and guide screens with button interactions."""

    # Constants
    BUTTON_SCALE = 0.3
    FONT_SIZE_TITLE = 74
    FONT_SIZE_BODY = 48

    # Button configurations
    BUTTON_CONFIG = {
        'start':   {'file': 'start.png',  'pos': (0.5, 0.60)},
        'guide':   {'file': 'guide.png',  'pos': (0.5, 0.73)},
        'credits': {'file': 'credit.png', 'pos': (0.5, 0.86)},
        'back':    {'file': 'back.png',   'pos': (0.08, 0.92)}
    }

    def __init__(self, screen, assets_dir='assets/images'):
        """
        Initialize menu manager.

        Args:
            screen: Pygame display surface
            assets_dir: Path to assets directory
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.assets_dir = assets_dir

        # Assets
        self.buttons = {}
        self.background = None
        self.credits_bg = None
        self.guide_bg = None

        # Sound manager (will be set from main.py)
        self.sound_manager = None

        # Fonts
        self.font_title = pygame.font.Font(None, self.FONT_SIZE_TITLE)
        self.font_body = pygame.font.Font(None, self.FONT_SIZE_BODY)

        self._load_assets()

    def _load_assets(self):
        """Load all menu assets (backgrounds and buttons)."""
        self._load_backgrounds()
        self._load_buttons()

    def _load_backgrounds(self):
        """Load background images for menu screens."""
        backgrounds = {
            'background': 'landing_page.png',
            'credits_bg': 'credit_page.png',
            'guide_bg': 'landing_page.png'  # Nanti diganti jika sudah ada pagenya
        }

        for attr_name, filename in backgrounds.items():
            path = os.path.join(self.assets_dir, filename)
            if os.path.exists(path):
                image = pygame.image.load(path).convert()
                scaled_image = pygame.transform.scale(
                    image,
                    (self.screen_width, self.screen_height)
                )
                setattr(self, attr_name, scaled_image)
            elif attr_name == 'background':
                # Main background is required
                print(f"[Warning] Background not found: {path}")

    def _load_buttons(self):
        """Load and scale button images."""
        for name, info in self.BUTTON_CONFIG.items():
            path = os.path.join(self.assets_dir, info['file'])

            if not os.path.exists(path):
                print(f"[Warning] Button asset not found: {path}")
                continue

            # Load and scale button
            image = pygame.image.load(path).convert_alpha()
            scaled_image = self._scale_image(image, self.BUTTON_SCALE)

            # Calculate button position
            center_x = int(self.screen_width * info['pos'][0])
            center_y = int(self.screen_height * info['pos'][1])
            rect = scaled_image.get_rect(center=(center_x, center_y))

            self.buttons[name] = {'image': scaled_image, 'rect': rect}

    def _scale_image(self, image, scale):
        """
        Scale image by given factor.

        Args:
            image: Pygame surface to scale
            scale: Scale factor (0.0 to 1.0+)

        Returns:
            Scaled pygame surface
        """
        original_size = image.get_size()
        new_size = (
            int(original_size[0] * scale),
            int(original_size[1] * scale)
        )
        return pygame.transform.smoothscale(image, new_size)

    def _draw_background(self, background_surface=None):
        """
        Draw background on screen.

        Args:
            background_surface: Custom background to draw, uses default if None
        """
        bg = background_surface or self.background
        if bg:
            self.screen.blit(bg, (0, 0))

    def _draw_buttons(self, button_names):
        """
        Draw specified buttons on screen.

        Args:
            button_names: List or tuple of button names to draw
        """
        for name in button_names:
            if name in self.buttons:
                btn = self.buttons[name]
                self.screen.blit(btn['image'], btn['rect'])

    def draw_menu(self):
        """Draw main menu screen."""
        self._draw_background()
        self._draw_buttons(('start', 'guide', 'credits'))

    def draw_credits_screen(self):
        """Draw credits screen with background and back button."""
        self._draw_background(self.credits_bg)
        self._draw_buttons(('back',))

    def draw_guide_screen(self):
        """Draw guide screen with background and back button."""
        self._draw_background(self.guide_bg)
        self._draw_buttons(('back',))

    def check_button_hover(self, hand_pos):
        """
        Check if hand position is hovering over any button.

        Args:
            hand_pos: Tuple (x, y) of hand position or None

        Returns:
            Button name if hovering, None otherwise
        """
        if hand_pos is None:
            return None

        for name, btn in self.buttons.items():
            if btn['rect'].collidepoint(hand_pos):
                return name

        return None

    def check_button_fist_click(self, hand_info):
        """
        Check if either hand is making a fist over any button.

        Args:
            hand_info: Dictionary with left_hand and right_hand info containing
                      position and is_fist status

        Returns:
            Button name if fist detected over button, None otherwise
        """
        # Check both hands
        for hand_key in ['left_hand', 'right_hand']:
            hand = hand_info.get(hand_key, {})
            hand_pos = hand.get('position')
            is_fist = hand.get('is_fist', False)

            # If hand is making fist and positioned over a button
            if is_fist and hand_pos:
                for name, btn in self.buttons.items():
                    if btn['rect'].collidepoint(hand_pos):
                        return name

        return None

    def play_button_sound(self):
        """Play button click sound if sound manager is available."""
        if self.sound_manager:
            self.sound_manager.play_sound('button')