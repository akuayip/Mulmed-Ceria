import pygame
import os

class MenuManager:
    """
    Mengelola tampilan Main Menu, Credits, dan Guide dengan background statis dan scaling otomatis.
    """

    def __init__(self, screen, assets_dir='assets/images'):
        self.screen = screen
        self.W = screen.get_width()
        self.H = screen.get_height()
        self.assets_dir = assets_dir
        self.buttons = {}
        self.bg_image = None

        # Font responsif 
        self.f_title = pygame.font.Font(None, int(self.H * 0.1))
        self.f_body = pygame.font.Font(None, int(self.H * 0.06))

        self._load_background()
        self._load_buttons()

    def _load_background(self):
        """Muat dan scale background menu."""
        bg_filename = 'landing_page.png' 
        path = os.path.join(self.assets_dir, bg_filename)
        
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert()
                self.bg_image = pygame.transform.scale(img, (self.W, self.H))
                print("Background menu loaded.")
            except Exception as e:
                 print(f"[Error] Gagal load background: {e}")
        else:
            print(f"[Warning] Background {bg_filename} tidak ditemukan. Pakai warna solid.")
            self.bg_image = pygame.Surface((self.W, self.H))
            self.bg_image.fill((50, 50, 80))

    def _load_buttons(self):
        """Muat dan scale tombol secara otomatis."""
        # Konfigurasi tombol (posisi relatif 0.0 - 1.0)
        button_cfg = {
            'start':   {'file': 'start.png',  'pos': (0.5, 0.60)}, 
            'guide':   {'file': 'guide.png',  'pos': (0.5, 0.75)},
            'credits': {'file': 'credit.png', 'pos': (0.5, 0.90)},
            'back':    {'file': 'back.png',    'pos': (0.1, 0.85)} 
        }

        # Tinggi target tombol (1/8 tinggi layar)
        target_btn_height = int(self.H / 8)

        for name, info in button_cfg.items():
            path = os.path.join(self.assets_dir, info['file'])
            if not os.path.exists(path):
                print(f"[Warning] Tombol {name} tidak ditemukan: {path}")
                continue
            
            try:
                img = pygame.image.load(path).convert_alpha()
                
                # Auto Scaling
                aspect = img.get_width() / img.get_height()
                new_width = int(target_btn_height * aspect)
                scaled_img = pygame.transform.smoothscale(img, (new_width, target_btn_height))

                rect = scaled_img.get_rect(center=(int(self.W * info['pos'][0]), int(self.H * info['pos'][1])))
                self.buttons[name] = {'image': scaled_img, 'rect': rect}
            except Exception as e:
                 print(f"[Error] Gagal load tombol {name}: {e}")

    def _draw_background(self):
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))

    def _draw_title(self, text, y_ratio=0.2):
        # Bayangan (opsional)
        shadow = self.f_title.render(text, True, (0, 0, 0))
        s_rect = shadow.get_rect(center=(self.W // 2 + 3, self.H * y_ratio + 3))
        self.screen.blit(shadow, s_rect)

        # Teks Utama
        title = self.f_title.render(text, True, (255, 255, 255))
        rect = title.get_rect(center=(self.W // 2, self.H * y_ratio))
        self.screen.blit(title, rect)

    # --- PUBLIC DRAW FUNCTIONS ---

    def draw_menu(self):
        self._draw_background()
        for name in ('start', 'guide', 'credits'):
            if name in self.buttons:
                self.screen.blit(self.buttons[name]['image'], self.buttons[name]['rect'])

    def draw_credits_screen(self):
        self._draw_background()
        
        # Load credit page background
        credit_bg_path = os.path.join(self.assets_dir, 'credit_page.png')
        if os.path.exists(credit_bg_path):
            try:
                credit_bg = pygame.image.load(credit_bg_path).convert()
                credit_bg = pygame.transform.scale(credit_bg, (self.W, self.H))
                self.screen.blit(credit_bg, (0, 0))
            except Exception as e:
                print(f"[Error] Gagal load credit page: {e}")

        if 'back' in self.buttons:
            self.screen.blit(self.buttons['back']['image'], self.buttons['back']['rect'])

    def draw_guide_screen(self):
        self._draw_background()
        self._draw_title("How to Play")

        guide_lines = [
            "Pukul target HIJAU (+Poin)",
            "Hindari bom MERAH (-Nyawa)",
            "Ambil power-up KUNING (Bonus)",
            "Gunakan jari telunjuk untuk kursor"
        ]

        y = self.H * 0.4
        for line in guide_lines:
            t = self.f_body.render(line, True, (220, 220, 220))
            rect = t.get_rect(center=(self.W // 2, y))

            bg_rect = rect.inflate(20, 10)
            s = pygame.Surface((bg_rect.width, bg_rect.height))
            s.set_alpha(150)
            s.fill((0,0,0))
            self.screen.blit(s, bg_rect.topleft)

            self.screen.blit(t, rect)
            y += int(self.H * 0.08)

        if 'back' in self.buttons:
            self.screen.blit(self.buttons['back']['image'], self.buttons['back']['rect'])

    # CEK HOVER
    def check_button_hover(self, hand_pos):
        if hand_pos is None:
            return None
        for name, btn in self.buttons.items():
            if btn['rect'].collidepoint(hand_pos):
                return name
        return None