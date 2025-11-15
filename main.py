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


def is_same_position(pos1, pos2, threshold=40):
    if pos1 is None or pos2 is None:
        return False
    return abs(pos1[0] - pos2[0]) < threshold and abs(pos1[1] - pos2[1]) < threshold


def main():
    SCREEN_W, SCREEN_H = 1280, 720
    FPS = 60

    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Cam-Fu - Pose Fighting Game")
    clock = pygame.time.Clock()

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

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Kamera tidak ditemukan.")
        sys.exit()

    current_state = GAME_MENU
    prev_hand = None
    click_timer = 0
    CLICK_HOLD = 0.5

    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        # Events
        for e in pygame.event.get():
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

        # Camera Read
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        cam_h, cam_w = frame.shape[:2]  # ukuran asli kamera
        _, landmarks = pose_detector.detect_pose(frame)

        # --- LANDMARK FIXED ---
        raw_hand = None
        if landmarks:
            raw_hand = pose_detector.get_landmark_position(
                landmarks,
                mp.solutions.pose.PoseLandmark.RIGHT_WRIST.value,
                cam_w,
                cam_h
            )

        # Scale to screen
        hand_pos = None
        if raw_hand:
            hand_pos = pose_detector.to_screen_coordinates(
                raw_hand[0], raw_hand[1],
                cam_w, cam_h,
                SCREEN_W, SCREEN_H
            )

        # Draw camera background
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_py = pygame.image.frombuffer(frame_rgb.tobytes(), frame.shape[1::-1], "RGB")
        frame_py = pygame.transform.scale(frame_py, (SCREEN_W, SCREEN_H))
        screen.blit(frame_py, (0, 0))

        # GAME STATE HANDLING
        if current_state == GAME_MENU:
            menu.draw_menu()
            hovered = menu.check_button_hover(hand_pos)

            if hovered and prev_hand and hovered == menu.check_button_hover(prev_hand) and is_same_position(hand_pos, prev_hand):
                click_timer += dt

                if click_timer >= CLICK_HOLD:
                    if hovered == "start":
                        current_state = GAME_PLAY
                        game_engine.reset_game()
                    elif hovered == "credits":
                        current_state = GAME_CREDITS
                    elif hovered == "guide":
                        current_state = GAME_GUIDE

                    click_timer = 0
            else:
                click_timer = 0

        elif current_state == GAME_PLAY:
            game_engine.update(dt, landmarks)
            game_engine.draw(landmarks)

            if game_engine.score_manager.game_over:
                current_state = GAME_OVER
                game_engine.sound_manager.stop_music()

        elif current_state == GAME_CREDITS:
            menu.draw_credits_screen()
            hovered = menu.check_button_hover(hand_pos)

            if hovered == "back" and prev_hand and hovered == menu.check_button_hover(prev_hand):
                click_timer += dt
                if click_timer >= CLICK_HOLD:
                    current_state = GAME_MENU
                    click_timer = 0
            else:
                click_timer = 0

        elif current_state == GAME_GUIDE:
            menu.draw_guide_screen()
            hovered = menu.check_button_hover(hand_pos)

            if hovered == "back" and prev_hand and hovered == menu.check_button_hover(prev_hand):
                click_timer += dt
                if click_timer >= CLICK_HOLD:
                    current_state = GAME_MENU
                    click_timer = 0
            else:
                click_timer = 0

        elif current_state == GAME_OVER:
            game_engine.draw(landmarks)
            game_renderer.draw_game_over_screen(game_engine.score_manager)

        pygame.display.flip()
        prev_hand = hand_pos

    cap.release()
    game_engine.cleanup()
    sys.exit()


if __name__ == "__main__":
    main()
