import pygame
import sys
import os
import cv2
import mediapipe as mp
import time  # PENTING: Untuk menghitung waktu main

# Import modul game
from game_engine import GameEngine
from pose_detector import PoseDetector
from renderer import GameRenderer
from spawn_manager import SpawnManager
from menu_manager import MenuManager
from sound_manager import SoundManager

# --- KONFIGURASI STATE GAME ---
GAME_MENU = 0
GAME_COUNTDOWN = 1
GAME_PLAY = 2
GAME_OVER = 3
GAME_CREDITS = 4
GAME_GUIDE = 5

pygame.init()
pygame.font.init()

# --- FUNGSI BANTUAN (UTILITY) ---
def is_same_position(pos1, pos2, threshold=80):
    if pos1 is None or pos2 is None:
        return False
    return abs(pos1[0] - pos2[0]) < threshold and abs(pos1[1] - pos2[1]) < threshold


def select_camera_terminal(available_cameras):
    """Menu pemilihan kamera via terminal."""
    print("\n" + "="*60)
    print("        PILIH KAMERA - CAM-FU")
    print("="*60)

    if not available_cameras:
        print("Error: Tidak ada kamera yang ditemukan!")
        return None

    print(f"\nKamera yang tersedia ({len(available_cameras)} kamera):")
    print("-" * 40)

    for i, cam_idx in enumerate(available_cameras, 1):
        print(f"{i}. Kamera {cam_idx}")

    print("\nKetik nomor kamera yang ingin digunakan (1-{}):".format(len(available_cameras)))
    print("Atau ketik 'q' untuk keluar")

    while True:
        try:
            choice = input("\nPilihan Anda: ").strip().lower()

            if choice == 'q':
                print("Pembatalan pemilihan kamera. Keluar dari aplikasi.")
                sys.exit(0)

            # Validasi input
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(available_cameras):
                    selected_camera = available_cameras[choice_idx]
                    print(f"\n✓ Kamera {selected_camera} telah dipilih!")
                    return selected_camera
                else:
                    print(
                        f"❌ Nomor tidak valid. Pilih antara 1-{len(available_cameras)} atau 'q' untuk keluar")
            except ValueError:
                print("❌ Input tidak valid. Masukkan nomor atau 'q' untuk keluar")

        except KeyboardInterrupt:
            print("\n\nPembatalan pemilihan kamera. Keluar dari aplikasi.")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error: {e}. Coba lagi.")


def select_camera_terminal_demo(available_cameras):
    """Demo terminal camera selection - untuk testing tanpa input interaktif."""
    print("\n" + "="*60)
    print("        DEMO PILIH KAMERA TERMINAL - CAM-FU")
    print("="*60)

    if not available_cameras:
        print("Error: Tidak ada kamera yang ditemukan!")
        return None

    print(f"\nKamera yang tersedia ({len(available_cameras)} kamera):")
    print("-" * 40)

    for i, cam_idx in enumerate(available_cameras, 1):
        print(f"{i}. Kamera {cam_idx}")

    print(f"\n✓ Auto-pilih kamera {available_cameras[0]} (demo mode)")
    return available_cameras[0]


def main():
    # --- SETUP LAYAR & ASSETS ---
    SCREEN_W, SCREEN_H = 1280, 720
    FPS = 60
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
    pygame.display.set_caption("Cam-Fu") 
    clock = pygame.time.Clock()

    # Asset Background Sendiri
    try:
        game_bg = pygame.image.load("assets/images/play_bg.jpg").convert()
    except FileNotFoundError:
        print("Warning: assets/images/play_bg.jpg tidak ditemukan.")
        game_bg = pygame.Surface((1280, 720)) 

    # --- INISIALISASI MODUL ---
    pose_detector = PoseDetector()
    game_renderer = GameRenderer(screen, assets_dir='assets/images')
    spawn_manager = SpawnManager(SCREEN_W, SCREEN_H)

    game_engine = GameEngine(
        screen=screen,
        pose_detector=pose_detector,
        game_renderer=game_renderer,
        spawn_manager=spawn_manager
    )

    menu = MenuManager(screen, 'assets/images')

    # Sound manager
    sound_manager = SoundManager()

    # Connect sound manager to menu
    menu.sound_manager = sound_manager

    # Camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Kamera tidak ditemukan.")
        sys.exit()

    # Setup Countdown 
    countdown_timer = 3.0
    countdown_images = {}
    for i in [1, 2, 3]:
        img_path = f'assets/images/cd_{i}.png' # Pastikan nama file sesuai (number_ atau cd_)
        if os.path.exists(img_path):
            img = pygame.image.load(img_path).convert_alpha()
            countdown_images[i] = pygame.transform.smoothscale(img, (200, 200))

    # Variabel Loop
    current_state = GAME_MENU

    # Countdown variables
    countdown_timer = 3.0
    countdown_images = {}

    # Load countdown images
    for i in [1, 2, 3]:
        img_path = f'assets/images/cd_{i}.png'
        if os.path.exists(img_path):
            img = pygame.image.load(img_path).convert_alpha()
            # Scale to appropriate size (200x200)
            countdown_images[i] = pygame.transform.smoothscale(img, (200, 200))
        else:
            print(f"[Warning] Countdown image not found: {img_path}")

    # Start menu music
    sound_manager.play_music('menu', loops=-1, fade_ms=1000)

    # Anti-spam mechanism for fist clicks
    last_fist_time = 0
    FIST_COOLDOWN = 0.5  # 500ms cooldown between fist clicks

    running = True

    # Variabel Waktu & Animasi
    start_time = 0
    play_duration = 0
    game_over_timer = 0.0  # Timer untuk animasi intro game over

    # --- GAME LOOP ---
    while running:
        dt = clock.tick(FPS) / 1000.0
        current_time = pygame.time.get_ticks() / 1000.0  # Current time in seconds

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
                
            elif e.type == pygame.VIDEORESIZE:
                SCREEN_W, SCREEN_H = e.w, e.h
                screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
                if hasattr(game_renderer, 'update_screen_size'):
                    game_renderer.update_screen_size(SCREEN_W, SCREEN_H)
                spawn_manager.update_screen_size(SCREEN_W, SCREEN_H)
                
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q:
                    running = False
                
                # Kontrol Volume 
                elif e.key == pygame.K_m: sound_manager.toggle_music()
                elif e.key == pygame.K_s: sound_manager.toggle_sound()
                elif e.key == pygame.K_PLUS or e.key == pygame.K_EQUALS:
                    sound_manager.set_music_volume(sound_manager.music_volume + 0.1)
                elif e.key == pygame.K_MINUS:
                    sound_manager.set_music_volume(sound_manager.music_volume - 0.1)
                
                # Navigasi Menu
                elif e.key == pygame.K_ESCAPE:
                    if current_state in (GAME_CREDITS, GAME_GUIDE, GAME_COUNTDOWN, GAME_PLAY):
                        current_state = GAME_MENU
                        sound_manager.crossfade_music('menu', fade_out_ms=500, fade_in_ms=500)
                        
                # Restart manual (hanya aktif setelah animasi intro selesai)
                elif current_state == GAME_OVER and game_over_timer > 2.5 and e.key == pygame.K_r:
                    current_state = GAME_COUNTDOWN
                    countdown_timer = 3.0
                    game_engine.reset_game()
                    sound_manager.stop_music()
                    sound_manager.play_sound('countdown')

        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        cam_h, cam_w = frame.shape[:2]
        _, landmarks = pose_detector.detect_pose(frame)

        active_hand_pos = None
        right_idx_pos = None
        left_idx_pos = None

        if landmarks:
            scale_x = SCREEN_W / 1280
            scale_y = SCREEN_H / 720

            raw_right = pose_detector.get_landmark_position(
                landmarks, mp.solutions.pose.PoseLandmark.RIGHT_INDEX.value, cam_w, cam_h)
            raw_left = pose_detector.get_landmark_position(
                landmarks, mp.solutions.pose.PoseLandmark.LEFT_INDEX.value, cam_w, cam_h)

            if raw_right:
                right_idx_pos = pose_detector.to_screen_coordinates(
                    raw_right[0] * scale_x, raw_right[1] * scale_y, 
                    cam_w, cam_h, SCREEN_W, SCREEN_H)
            if raw_left:
                left_idx_pos = pose_detector.to_screen_coordinates(
                    raw_left[0] * scale_x, raw_left[1] * scale_y, 
                    cam_w, cam_h, SCREEN_W, SCREEN_H)

            # Cek hover
            hover_right = menu.check_button_hover(right_idx_pos) if current_state != GAME_PLAY else None
            hover_left = menu.check_button_hover(left_idx_pos) if current_state != GAME_PLAY else None

            if hover_right: active_hand_pos = right_idx_pos
            elif hover_left: active_hand_pos = left_idx_pos
            elif right_idx_pos: active_hand_pos = right_idx_pos
            elif left_idx_pos: active_hand_pos = left_idx_pos

        # Draw Background (Hanya saat Gameplay/Countdown)
        # Game Over punya background sendiri di renderer
        if current_state in (GAME_PLAY, GAME_COUNTDOWN):
            bg_scaled = pygame.transform.scale(game_bg, (SCREEN_W, SCREEN_H))
            screen.blit(bg_scaled, (0, 0))
        elif current_state != GAME_OVER:
            # Menu/Guide/Credits pakai kamera
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_py = pygame.image.frombuffer(
                frame_rgb.tobytes(), frame.shape[1::-1], "RGB")
            frame_py = pygame.transform.scale(frame_py, (SCREEN_W, SCREEN_H))
            screen.blit(frame_py, (0, 0))

        
        # --- MENU ---
        if current_state == GAME_MENU:
            # Ensure menu music is playing
            if sound_manager.current_music != 'menu':
                sound_manager.crossfade_music(
                    'menu', fade_out_ms=500, fade_in_ms=500)

            menu.draw_menu()

            # Get hand info for fist detection
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            hand_info = pose_detector.get_hand_info(
                frame_rgb, SCREEN_W, SCREEN_H)

            # Check for fist click on buttons (with cooldown)
            fist_button = menu.check_button_fist_click(hand_info)
            if fist_button and (current_time - last_fist_time) > FIST_COOLDOWN:
                last_fist_time = current_time
                menu.play_button_sound()
                if fist_button == "start":
                    current_state = GAME_COUNTDOWN
                    countdown_timer = 3.0
                    game_engine.reset_game()
                    sound_manager.stop_music()
                    sound_manager.play_sound('countdown')
                elif fist_button == "credits":
                    current_state = GAME_CREDITS
                elif fist_button == "guide":
                    current_state = GAME_GUIDE

        # --- COUNTDOWN ---
        elif current_state == GAME_COUNTDOWN:
            dark_overlay = pygame.Surface((SCREEN_W, SCREEN_H))
            dark_overlay.set_alpha(180)
            dark_overlay.fill((0, 0, 0))
            screen.blit(dark_overlay, (0, 0))
            
            countdown_timer -= dt
            
            if countdown_timer > 2.0: num = 3
            elif countdown_timer > 1.0: num = 2
            elif countdown_timer > 0.0: num = 1
            else:
                current_state = GAME_PLAY
                sound_manager.play_music('gameplay')
                # RESET Timer
                start_time = time.time()
                game_over_timer = 0.0 
                continue
            
            if num in countdown_images:
                img = countdown_images[num]
                img_rect = img.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2))
                screen.blit(img, img_rect)
            else:
                font_cd = pygame.font.Font(None, 200)
                text = font_cd.render(str(num), True, (255, 255, 255))
                text_rect = text.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2))
                screen.blit(text, text_rect)

        # --- GAMEPLAY ---
        elif current_state == GAME_PLAY:
            # Hitung waktu main
            play_duration = time.time() - start_time

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            hand_info = pose_detector.get_hand_info(frame_rgb, SCREEN_W, SCREEN_H)
            
            game_engine.update(dt, landmarks, hand_info)

            # Background already drawn above in "Background Rendering" section
            
            game_engine.renderer.draw_game_objects(
                game_engine.targets,
                game_engine.obstacles,
                game_engine.powerups)
            
            if landmarks:
                game_engine.renderer.draw_stickman(landmarks, pose_detector)
            
            game_engine.renderer.draw_hand_indicators(hand_info)
            game_engine.renderer.draw_ui(game_engine.score_manager, clock, hand_info)
            
            if game_engine.score_manager.game_over:
                current_state = GAME_OVER
                game_engine.sound_manager.stop_music()
                game_over_timer = 0.0 

        # --- SUB-MENU ---
        elif current_state in (GAME_CREDITS, GAME_GUIDE):
            if current_state == GAME_CREDITS:
                menu.draw_credits_screen()
            else:
                menu.draw_guide_screen()
                
            hovered = menu.check_button_hover(active_hand_pos)
            if hovered == "back" and stable_hover(active_hand_pos, prev_hand, 100):
                click_timer += dt
                if click_timer >= CLICK_HOLD:
                    menu.play_button_sound()
                    current_state = GAME_MENU
                    click_timer = 0.0
            else:
                click_timer = 0.0

        # --- GAME OVER (SEQUENTIAL) ---
        elif current_state == GAME_OVER:
            # Tambah timer
            game_over_timer += dt
            
            # PHASE 1: 0 - 2.5 Detik (Intro Hitam)
            if game_over_timer < 2.5:
                game_renderer.draw_game_over_screen(
                    game_engine.score_manager, 
                    play_duration=play_duration, 
                    phase=1 # Kirim sinyal fase 1
                )
            
            # PHASE 2: Setelah 2.5 Detik (Background + Menu)
            else:
                game_renderer.draw_game_over_screen(
                    game_engine.score_manager, 
                    play_duration=play_duration, 
                    phase=2 # Kirim sinyal fase 2
                )
                
                # Logic Tombol Menu (Hanya aktif di Phase 2)
                # Area tombol menu (Estimasi posisi sesuai renderer)
                menu_rect = pygame.Rect(30, SCREEN_H - 130, 100, 100) 
                
                hovering_menu = False
                if active_hand_pos:
                    cursor_rect = pygame.Rect(active_hand_pos[0]-10, active_hand_pos[1]-10, 20, 20)
                    if menu_rect.colliderect(cursor_rect):
                        hovering_menu = True
                
                if hovering_menu and stable_hover(active_hand_pos, prev_hand, 100):
                    click_timer += dt
                    if click_timer >= CLICK_HOLD:
                        menu.play_button_sound()
                        current_state = GAME_MENU
                        click_timer = 0.0
                else:
                    click_timer = 0.0

        # RENDER KURSOR (Kecuali Gameplay)
        if current_state != GAME_PLAY:
            if right_idx_pos:
                pygame.draw.circle(screen, (150, 150, 150),
                                   right_idx_pos, 10, 2)
            if left_idx_pos:
                pygame.draw.circle(screen, (150, 150, 150),
                                   left_idx_pos, 10, 2)

            if active_hand_pos:
                pygame.draw.circle(screen, (0, 255, 255), active_hand_pos, 20, 3)
                if click_timer > 0:
                    progress = min(click_timer / CLICK_HOLD, 1.0)
                    radius = int(20 * progress)
                    pygame.draw.circle(screen, (0, 255, 0), active_hand_pos, radius)

        pygame.display.flip()

    cap.release()
    sound_manager.cleanup()
    game_engine.cleanup()
    sys.exit()


if __name__ == "__main__":
    main()