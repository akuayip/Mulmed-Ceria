import pygame
import sys
import cv2
import mediapipe as mp

from game_engine import GameEngine
from pose_detector import PoseDetector
from renderer import GameRenderer
from spawn_manager import SpawnManager
from menu_manager import MenuManager


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
    screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    SCREEN_W, SCREEN_H = screen.get_size()
    fullscreen = False
    pygame.display.set_caption("Cam-Fu")
    clock = pygame.time.Clock()

    game_bg = pygame.image.load("assets/images/play_bg.jpg").convert()
    pose_detector = PoseDetector()
    game_renderer = GameRenderer(screen)
    spawn_manager = SpawnManager(SCREEN_W, SCREEN_H)
    game_engine = GameEngine(screen, pose_detector, game_renderer, spawn_manager)
    menu = MenuManager(screen, 'assets/images')

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Kamera tidak ditemukan.")
        sys.exit()

    current_state = GAME_MENU
    prev_hand = None
    click_timer = 0.0
    CLICK_HOLD = 0.8

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.VIDEORESIZE:
                SCREEN_W, SCREEN_H = e.w, e.h
                screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
                menu = MenuManager(screen, 'assets/images')
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q:
                    running = False
                if e.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
                if e.key == pygame.K_ESCAPE and fullscreen:
                    fullscreen = False
                    screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
                if e.key == pygame.K_m:
                    current_state = GAME_MENU
                    game_engine.sound_manager.stop_music()
                if current_state == GAME_OVER and e.key == pygame.K_r:
                    current_state = GAME_PLAY
                    game_engine.reset_game()

        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        cam_h, cam_w = frame.shape[:2]
        _, landmarks = pose_detector.detect_pose(frame)

        active_hand_pos = None
        right_idx_pos, left_idx_pos = None, None

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hand_info = pose_detector.get_hand_info(frame_rgb, cam_w, cam_h)

        if landmarks:
            raw_right_idx = pose_detector.get_landmark_position(
                landmarks, mp.solutions.pose.PoseLandmark.RIGHT_INDEX.value, cam_w, cam_h)
            raw_left_idx = pose_detector.get_landmark_position(
                landmarks, mp.solutions.pose.PoseLandmark.LEFT_INDEX.value, cam_w, cam_h)

            if raw_right_idx:
                right_idx_pos = pose_detector.to_screen_coordinates(*raw_right_idx, cam_w, cam_h, SCREEN_W, SCREEN_H)
            if raw_left_idx:
                left_idx_pos = pose_detector.to_screen_coordinates(*raw_left_idx, cam_w, cam_h, SCREEN_W, SCREEN_H)

            raw_right_wrist = pose_detector.get_landmark_position(
                landmarks, mp.solutions.pose.PoseLandmark.RIGHT_WRIST.value, cam_w, cam_h)
            raw_left_wrist = pose_detector.get_landmark_position(
                landmarks, mp.solutions.pose.PoseLandmark.LEFT_WRIST.value, cam_w, cam_h)

            if raw_right_wrist:
                hand_info['right_hand']['position'] = pose_detector.to_screen_coordinates(
                    *raw_right_wrist, cam_w, cam_h, SCREEN_W, SCREEN_H)
            if raw_left_wrist:
                hand_info['left_hand']['position'] = pose_detector.to_screen_coordinates(
                    *raw_left_wrist, cam_w, cam_h, SCREEN_W, SCREEN_H)

            hover_right = menu.check_button_hover(right_idx_pos) if current_state != GAME_PLAY else None
            hover_left = menu.check_button_hover(left_idx_pos) if current_state != GAME_PLAY else None

            active_hand_pos = hover_right and right_idx_pos or hover_left and left_idx_pos or right_idx_pos or left_idx_pos
        
        SCREEN_W, SCREEN_H = screen.get_size()

        if current_state == GAME_PLAY:
            bg_scaled = pygame.transform.scale(game_bg, (SCREEN_W, SCREEN_H))
            screen.blit(bg_scaled, (0, 0))
        else:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_py = pygame.transform.scale(
                pygame.image.frombuffer(frame_rgb.tobytes(), frame.shape[1::-1], "RGB"),
                (SCREEN_W, SCREEN_H))
            screen.blit(frame_py, (0, 0))

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

            bg_scaled = pygame.transform.scale(game_bg, (SCREEN_W, SCREEN_H))
            screen.blit(bg_scaled, (0, 0))

            game_engine.update(dt, landmarks, hand_info)

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

        elif current_state == GAME_CREDITS:
            menu.draw_credits_screen()
            if menu.check_button_hover(active_hand_pos) == "back" and stable_hover(active_hand_pos, prev_hand, 100):
                click_timer += dt
                if click_timer >= CLICK_HOLD:
                    current_state = GAME_MENU
                    click_timer = 0.0
            else:
                click_timer = 0.0

        elif current_state == GAME_GUIDE:
            menu.draw_guide_screen()
            if menu.check_button_hover(active_hand_pos) == "back" and stable_hover(active_hand_pos, prev_hand, 100):
                click_timer += dt
                if click_timer >= CLICK_HOLD:
                    current_state = GAME_MENU
                    click_timer = 0.0
            else:
                click_timer = 0.0

        elif current_state == GAME_OVER:
            game_renderer.draw_game_over_screen(game_engine.score_manager)

        if current_state != GAME_PLAY:
            if right_idx_pos:
                pygame.draw.circle(screen, (150, 150, 150), right_idx_pos, 10, 2)
            if left_idx_pos:
                pygame.draw.circle(screen, (150, 150, 150), left_idx_pos, 10, 2)

            if active_hand_pos:
                pygame.draw.circle(screen, (0, 255, 255), active_hand_pos, 20, 3)
                if click_timer > 0:
                    pygame.draw.circle(screen, (0, 255, 0), active_hand_pos,
                        int(20 * min(click_timer / CLICK_HOLD, 1.0)))

        pygame.display.flip()
        prev_hand = active_hand_pos

    cap.release()
    game_engine.cleanup()
    sys.exit()

if __name__ == "__main__":
    main()
