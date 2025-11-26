import pygame
import os
from typing import Optional, Tuple



class MenuManager:
    """Manages main menu, credits, and guide screens with buttons & backgrounds."""

    # Konfigurasi tombol
    BUTTON_CONFIG = {
        'start':   {'file': 'start.png',  'pos': (0.5, 0.60)},
        'guide':   {'file': 'guide.png',  'pos': (0.5, 0.75)},
        'credits': {'file': 'credit.png', 'pos': (0.5, 0.90)},
        'back':    {'file': 'back.png',   'pos': (0.10, 0.88)}
    }

    def __init__(self, screen: pygame.Surface, assets_dir: str = 'assets/images') -> None:
        """Initialize menu manager with screen and assets directory."""
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.assets_dir = assets_dir

        # Buttons & backgrounds
        self.buttons = {}
        self.bg_menu = None
        self.bg_credits = None
        self.bg_guide = None

        self.sound_manager = None

        # Fonts
        self.font_title = pygame.font.Font(None, int(self.screen_height * 0.10))
        self.font_body = pygame.font.Font(None, int(self.screen_height * 0.06))

        # Load semua aset
        self._load_backgrounds()
        self._load_buttons()

    # ASSET LOADING

    def _load_backgrounds(self) -> None:
        """Load backgrounds for menu, credits, and guide."""

        bg_files = {
            "bg_menu": "landing_page.png",
            "bg_credits": "credit_page.png",
            "bg_guide": "landing_page.png"  # nanti diganti kalau punya
        }

        for attr, filename in bg_files.items():
            path = os.path.join(self.assets_dir, filename)
            if os.path.exists(path):
                img = pygame.image.load(path).convert()
                scaled = pygame.transform.scale(img, (self.screen_width, self.screen_height))
                setattr(self, attr, scaled)
            else:
                print(f"[Warning] Background missing: {path}")
                setattr(self, attr, None)

    def _load_buttons(self) -> None:
        """Load and scale buttons based on configuration."""
        target_height = int(self.screen_height / 8)

        for name, info in self.BUTTON_CONFIG.items():
            path = os.path.join(self.assets_dir, info['file'])

            if not os.path.exists(path):
                print(f"[Warning] Button asset not found: {path}")
                continue

            try:
                img = pygame.image.load(path).convert_alpha()
                aspect = img.get_width() / img.get_height()
                new_width = int(target_height * aspect)
                scaled = pygame.transform.smoothscale(img, (new_width, target_height))

                cx = int(self.screen_width * info['pos'][0])
                cy = int(self.screen_height * info['pos'][1])
                rect = scaled.get_rect(center=(cx, cy))

                self.buttons[name] = {"image": scaled, "rect": rect}

            except Exception as e:
                print(f"[Error] Failed to load button {name}: {e}")

    # DRAWING HELPERS

    def _draw_background(self, bg):
        if bg:
            self.screen.blit(bg, (0, 0))

    def _draw_buttons(self, names):
        for name in names:
            if name in self.buttons:
                btn = self.buttons[name]
                self.screen.blit(btn['image'], btn['rect'])

    def _draw_title(self, text, y_ratio=0.18):
        shadow = self.font_title.render(text, True, (0, 0, 0))
        sh_rect = shadow.get_rect(center=(self.screen_width//2 + 3,
                                          int(self.screen_height * y_ratio) + 3))
        self.screen.blit(shadow, sh_rect)

        title = self.font_title.render(text, True, (255, 255, 255))
        t_rect = title.get_rect(center=(self.screen_width//2,
                                        int(self.screen_height * y_ratio)))
        self.screen.blit(title, t_rect)

    # PUBLIC DRAW FUNCTIONS (called from main.py)

    def draw_menu(self) -> None:
        self._draw_background(self.bg_menu)
        self._draw_buttons(('start', 'guide', 'credits'))

    def draw_credits_screen(self) -> None:
        self._draw_background(self.bg_credits)
        self._draw_buttons(('back',))

    def draw_guide_screen(self) -> None:
        self._draw_background(self.bg_guide)
        self._draw_title("How to Play")

        guide_texts = [
            "Pukul target HIJAU (+Poin)",
            "Hindari bom MERAH (-Nyawa)",
            "Ambil power-up KUNING (Bonus)",
            "Gunakan jari telunjuk untuk kursor"
        ]

        y = int(self.screen_height * 0.38)
        for line in guide_texts:
            txt = self.font_body.render(line, True, (230, 230, 230))
            rect = txt.get_rect(center=(self.screen_width//2, y))

            bg = rect.inflate(20, 10)
            s = pygame.Surface((bg.width, bg.height))
            s.set_alpha(130)
            s.fill((0, 0, 0))
            self.screen.blit(s, bg.topleft)

            self.screen.blit(txt, rect)
            y += int(self.screen_height * 0.08)

        self._draw_buttons(('back',))

    # Interaction

    def check_button_hover(self, hand_pos: Optional[Tuple[int, int]]) -> Optional[str]:
        """Return button name if hovered, else None."""
        if hand_pos is None:
            return None
        
        for name, btn in self.buttons.items():
            if btn["rect"].collidepoint(hand_pos):
                return name
        
        return None

    def play_button_sound(self) -> None:
        if self.sound_manager:
            self.sound_manager.play_sound('button')

