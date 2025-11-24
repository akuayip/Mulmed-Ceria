import pygame
import sys
import cv2
import mediapipe as mp

from game_engine import GameEngine
from pose_detector import PoseDetector
from renderer import GameRenderer
from spawn_manager import SpawnManager
from menu_manager import MenuManager

# Game States
GAME_MENU = 0
GAME_PLAY = 1
GAME_OVER = 2
GAME_CREDITS = 3
GAME_GUIDE = 4

pygame.init()
pygame.font.init()

def is_same_position(pos1, pos2, threshold=80):
    if pos1 is None or pos2 is None:
        return False
    return abs(pos1[0] - pos2[0]) < threshold and abs(pos1[1] - pos2[1]) < threshold

def stable_hover(current_pos, prev_pos, threshold=80):
    if current_pos is None:
        return False
    if prev_pos is None:
        return True
    return is_same_position(current_pos, prev_pos, threshold)

def main():
    SCREEN_W, SCREEN_H = 1280, 720
    FPS = 60
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
    pygame.display.set_caption("Cam-Fu - Pose Fighting Game")
    clock = pygame.time.Clock()

    # Core modules
    pose_detector = PoseDetector()
    game_renderer = GameRenderer(screen)
    spawn_manager = SpawnManager(SCREEN_W, SCREEN_H)
    
    game_engine = GameEngine(
        screen=screen,
        pose_detector=pose_detector,
        game_renderer=game_renderer,
        spawn_manager=spawn_manager
    )

    menu = MenuManager(screen, 'assets/images')

    # Camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Kamera tidak ditemukan.")
        sys.exit()

    # Input states
    current_state = GAME_MENU
    prev_hand = None
    click_timer = 0.0
    CLICK_HOLD = 0.8
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        # Event Handling
        for e in pygame.event.get():
            if e.type == pygame.VIDEORESIZE:
                SCREEN_W, SCREEN_H = e.w, e.h
                screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
                game_renderer.update_screen_size(SCREEN_W, SCREEN_H)
                spawn_manager.update_screen_size(SCREEN_W, SCREEN_H)
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q:
                    running = False
                if e.key == pygame.K_m:
                    current_state = GAME_MENU
                    game_engine.sound_manager.stop_music()
                if current_state == GAME_OVER and e.key == pygame.K_r:
                    current_state = GAME_PLAY
                    game_engine.reset_game()

        # Read Camera
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        cam_h, cam_w = frame.shape[:2]
        _, landmarks = pose_detector.detect_pose(frame)

        # Hand Tracking / Cursor System
        active_hand_pos = None
        right_idx_pos = None
        left_idx_pos = None

        if landmarks:
            raw_right = pose_detector.get_landmark_position(
                landmarks, mp.solutions.pose.PoseLandmark.RIGHT_INDEX.value, cam_w, cam_h
            )
            raw_left = pose_detector.get_landmark_position(
                landmarks, mp.solutions.pose.PoseLandmark.LEFT_INDEX.value, cam_w, cam_h
            )

            if raw_right:
                scale_x = SCREEN_W / 1280
                scale_y = SCREEN_H / 720

                right_idx_pos = pose_detector.to_screen_coordinates(
                    raw_right[0]*scale_x, raw_right[1]*scale_y,
                    cam_w, cam_h, SCREEN_W, SCREEN_H
                )
            if raw_left:
                scale_x = SCREEN_W / 1280
                scale_y = SCREEN_H / 720

                left_idx_pos = pose_detector.to_screen_coordinates(
                    raw_left[0]*scale_x, raw_left[1]*scale_y,
                    cam_w, cam_h, SCREEN_W, SCREEN_H
                )

            # Only check hover when NOT in gameplay
            hover_right = menu.check_button_hover(right_idx_pos) if current_state != GAME_PLAY else None
            hover_left = menu.check_button_hover(left_idx_pos) if current_state != GAME_PLAY else None

            if hover_right:
                active_hand_pos = right_idx_pos
            elif hover_left:
                active_hand_pos = left_idx_pos
            elif right_idx_pos:
                active_hand_pos = right_idx_pos
            elif left_idx_pos:
                active_hand_pos = left_idx_pos

        # Background Rendering
        if current_state == GAME_PLAY:
            screen.fill((0, 0, 0))   # Black background for gameplay
        else:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_py = pygame.image.frombuffer(frame_rgb.tobytes(), frame.shape[1::-1], "RGB")
            frame_py = pygame.transform.scale(frame_py, (SCREEN_W, SCREEN_H))
            screen.blit(frame_py, (0, 0))

        # Game State Machine
        if current_state == GAME_MENU:
            menu.draw_menu()
            hovered = menu.check_button_hover(active_hand_pos)

            if hovered and stable_hover(active_hand_pos, prev_hand, 100):
                click_timer += dt
                if click_timer >= CLICK_HOLD:
                    if hovered == "start":
                        current_state = GAME_PLAY
                        game_engine.reset_game()
                    elif hovered == "credits":
                        current_state = GAME_CREDITS
                    elif hovered == "guide":
                        current_state = GAME_GUIDE
                    click_timer = 0.0
            else:
                click_timer = 0.0

        elif current_state == GAME_PLAY:
            # Detect hands and get fist status
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            hand_info = pose_detector.get_hand_info(
                frame_rgb,
                SCREEN_W,
                SCREEN_H
            )
            
            game_engine.update(dt, landmarks, hand_info)
            
            # Draw game elements
            game_renderer.draw_game_objects(game_engine.targets, game_engine.obstacles, game_engine.powerups)
            
            if landmarks:
                game_renderer.draw_stickman(landmarks, pose_detector)
            
            game_renderer.draw_hand_indicators(hand_info)
            game_renderer.draw_ui(game_engine.score_manager, clock, hand_info)
            
            if game_engine.score_manager.game_over:
                current_state = GAME_OVER
                game_engine.sound_manager.stop_music()

        elif current_state == GAME_CREDITS:
            menu.draw_credits_screen()
            hovered = menu.check_button_hover(active_hand_pos)
            if hovered == "back" and stable_hover(active_hand_pos, prev_hand, 100):
                click_timer += dt
                if click_timer >= CLICK_HOLD:
                    current_state = GAME_MENU
                    click_timer = 0.0
            else:
                click_timer = 0.0

        elif current_state == GAME_GUIDE:
            menu.draw_guide_screen()
            hovered = menu.check_button_hover(active_hand_pos)
            if hovered == "back" and stable_hover(active_hand_pos, prev_hand, 100):
                click_timer += dt
                if click_timer >= CLICK_HOLD:
                    current_state = GAME_MENU
                    click_timer = 0.0
            else:
                click_timer = 0.0

        elif current_state == GAME_OVER:
            # Draw game elements with game over overlay
            game_renderer.draw_game_objects(game_engine.targets, game_engine.obstacles, game_engine.powerups)
            
            if landmarks:
                game_renderer.draw_stickman(landmarks, pose_detector)
            
            # hand_info untuk game over screen (kosong jika tidak ada)
            empty_hand_info = {
                'left_hand': {'position': None, 'is_fist': False},
                'right_hand': {'position': None, 'is_fist': False}
            }
            game_renderer.draw_ui(game_engine.score_manager, clock, empty_hand_info)

        # Cursor Rendering (Hidden During Gameplay)
        if current_state != GAME_PLAY:

            if right_idx_pos:
                pygame.draw.circle(screen, (150, 150, 150), right_idx_pos, 10, 2)
            if left_idx_pos:
                pygame.draw.circle(screen, (150, 150, 150), left_idx_pos, 10, 2)

            if active_hand_pos:
                pygame.draw.circle(screen, (0, 255, 255), active_hand_pos, 20, 3)

                if click_timer > 0:
                    progress = min(click_timer / CLICK_HOLD, 1.0)
                    radius = int(20 * progress)
                    pygame.draw.circle(screen, (0, 255, 0), active_hand_pos, radius)

        pygame.display.flip()
        prev_hand = active_hand_pos

    cap.release()
    game_engine.cleanup()
    sys.exit()

if __name__ == "__main__":
    main()
