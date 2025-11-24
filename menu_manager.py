import pygame
import os

class MenuManager:
    """Mengelola Main Menu, Credits, dan Guide."""

    def __init__(self, screen, assets_dir='assets/images'):
        self.screen = screen
        self.W = screen.get_width()
        self.H = screen.get_height()
        self.assets_dir = assets_dir
        self.buttons = {}

        # Font
        self.f_title = pygame.font.Font(None, 74)
        self.f_body = pygame.font.Font(None, 48)

        self._load_assets()

    # Load tombol
    def _load_assets(self):
        button_cfg = {
            'start':   {'file': 'start.png',  'pos': (0.5, 0.45)},
            'guide':   {'file': 'guide.png',  'pos': (0.5, 0.60)},
            'credits': {'file': 'credit.png', 'pos': (0.5, 0.75)},
            'back':    {'file': 'bom.png',    'pos': (0.15, 0.9)} 
        }

        for name, info in button_cfg.items():
            path = os.path.join(self.assets_dir, info['file'])
            if not os.path.exists(path):
                print(f"[Warning] Aset tombol tidak ditemukan: {path}")
                continue
            
            img = pygame.image.load(path).convert_alpha()
            rect = img.get_rect(center=(int(self.W * info['pos'][0]), int(self.H * info['pos'][1])))
            self.buttons[name] = {'image': img, 'rect': rect}

    # Helper: draw title text
    def _draw_title(self, text):
        title = self.f_title.render(text, True, (255, 255, 255))
        rect = title.get_rect(center=(self.W // 2, self.H * 0.2))
        self.screen.blit(title, rect)

    # MAIN MENU
    def draw_menu(self):
        self._draw_title("CAM-FU")
        for name in ('start', 'guide', 'credits'):
            if name in self.buttons:
                self.screen.blit(self.buttons[name]['image'], self.buttons[name]['rect'])

    # CREDITS SCREEN
    def draw_credits_screen(self):
        self._draw_title("Credits")

        credit_lines = [
            "Game oleh: Cindy Nadila Putri",
            "Dibantu oleh: Gemini",
            "Aset: (isi sumber aset)",
            "Powered by Pygame & MediaPipe"
        ]

        y = self.H * 0.4
        for line in credit_lines:
            t = self.f_body.render(line, True, (220, 220, 220))
            rect = t.get_rect(center=(self.W // 2, y))
            self.screen.blit(t, rect)
            y += 50

        if 'back' in self.buttons:
            self.screen.blit(self.buttons['back']['image'], self.buttons['back']['rect'])

    # GUIDE SCREEN
    def draw_guide_screen(self):
        self._draw_title("Guide")

        guide_lines = [
            "Pukul target HIJAU dengan tangan.",
            "Hindari bom MERAH.",
            "Ambil power-up KUNING untuk bonus.",
            "Tahan tangan untuk memilih tombol."
        ]

        y = self.H * 0.4
        for line in guide_lines:
            t = self.f_body.render(line, True, (220, 220, 220))
            rect = t.get_rect(center=(self.W // 2, y))
            self.screen.blit(t, rect)
            y += 50

        if 'back' in self.buttons:
            self.screen.blit(self.buttons['back']['image'], self.buttons['back']['rect'])

    # BUTTON HOVER
    def check_button_hover(self, hand_pos):
        if hand_pos is None:
            return None

        for name, btn in self.buttons.items():
            if btn['rect'].collidepoint(hand_pos):
                return name

        return None
