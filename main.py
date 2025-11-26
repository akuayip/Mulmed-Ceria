"""
Cam-Fu - Pose Fighting Game
Main entry point with clean architecture.
"""
import pygame
import sys
import cv2

# Configuration
import config

# Managers
from managers.camera_manager import CameraManager
from managers.sound_manager import SoundManager
from managers.menu_manager import MenuManager
from managers.spawn_manager import SpawnManager
from managers.score_manager import ScoreManager

# Detection
from detection.pose_detector import PoseDetector
from detection.collision_detector import CollisionDetector

# Rendering
from rendering.renderer import GameRenderer

# Core
from core.game_state_manager import GameStateManager

# States
from states.menu_state import MenuState
from states.countdown_state import CountdownState
from states.gameplay_state import GameplayState
from states.game_over_state import GameOverState
from states.credits_state import CreditsState
from states.guide_state import GuideState

# Game Engine
from game_engine import GameEngine


def main():
    """Main game loop."""
    # Initialize Pygame
    pygame.init()
    pygame.font.init()
    
    # Create screen
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Cam-Fu - Pose Fighting Game")
    clock = pygame.time.Clock()
    
    # Initialize camera
    try:
        camera = CameraManager(camera_id=0)
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Initialize managers
    sound_manager = SoundManager()
    pose_detector = PoseDetector()
    spawn_manager = SpawnManager(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    menu_manager = MenuManager(screen, config.IMAGES_DIR)
    menu_manager.sound_manager = sound_manager
    
    # Initialize renderer
    game_renderer = GameRenderer(screen, config.IMAGES_DIR)
    
    # Initialize game engine
    game_engine = GameEngine(
        screen=screen,
        pose_detector=pose_detector,
        game_renderer=game_renderer,
        spawn_manager=spawn_manager
    )
    
    # Initialize state manager
    state_manager = GameStateManager(screen, sound_manager)
    
    # Create all states
    states = {
        config.GAME_MENU: MenuState(screen, sound_manager, menu_manager),
        config.GAME_COUNTDOWN: CountdownState(screen, sound_manager, game_renderer),
        config.GAME_PLAY: GameplayState(screen, sound_manager, game_engine, game_renderer),
        config.GAME_OVER: GameOverState(screen, sound_manager, game_engine, game_renderer),
        config.GAME_CREDITS: CreditsState(screen, sound_manager, menu_manager),
        config.GAME_GUIDE: GuideState(screen, sound_manager, menu_manager)
    }
    
    state_manager.initialize_states(states)
    
    # Main game loop
    running = True
    while running:
        dt = clock.tick(config.FPS) / 1000.0
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                game_renderer.update_screen_size(event.w, event.h)
                spawn_manager.update_screen_size(event.w, event.h)
            
            elif event.type == pygame.KEYDOWN:
                # Global hotkeys
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_m:
                    sound_manager.toggle_music()
                elif event.key == pygame.K_s:
                    sound_manager.toggle_sound()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    new_vol = sound_manager.music_volume + 0.1
                    sound_manager.set_music_volume(new_vol)
                elif event.key == pygame.K_MINUS:
                    new_vol = sound_manager.music_volume - 0.1
                    sound_manager.set_music_volume(new_vol)
                else:
                    # Pass event to current state
                    state_manager.handle_event(event)
            else:
                state_manager.handle_event(event)
        
        # Get camera frame
        frame = camera.get_frame()
        if frame is None:
            print("Error: Could not read camera frame")
            break
        
        # Detect pose
        frame_rgb, landmarks = pose_detector.detect_pose(frame)
        
        # Get hand info
        hand_info = pose_detector.get_hand_info(
            frame_rgb,
            screen.get_width(),
            screen.get_height()
        )
        
        # Draw camera background for menu states
        if state_manager.current_state_id in (config.GAME_MENU, config.GAME_CREDITS, config.GAME_GUIDE):
            frame_py = pygame.image.frombuffer(frame_rgb.tobytes(), frame.shape[1::-1], "RGB")
            frame_py = pygame.transform.scale(frame_py, (screen.get_width(), screen.get_height()))
            screen.blit(frame_py, (0, 0))
        
        # Update current state
        state_manager.update(dt, landmarks, hand_info)
        
        # Render current state
        state_manager.render()
        
        # Special rendering for gameplay state
        if state_manager.current_state_id == config.GAME_PLAY:
            gameplay_state = states[config.GAME_PLAY]
            gameplay_state.render_with_landmarks(landmarks, hand_info, clock)
        
        # Draw cursor for non-gameplay states
        if state_manager.current_state_id != config.GAME_PLAY:
            from utils.helpers import get_active_hand_position, draw_progress_circle
            
            active_hand_pos = get_active_hand_position(hand_info)
            
            # Draw hand cursors
            if hand_info['right_hand']['position']:
                pygame.draw.circle(screen, config.GRAY, hand_info['right_hand']['position'], 10, 2)
            if hand_info['left_hand']['position']:
                pygame.draw.circle(screen, config.GRAY, hand_info['left_hand']['position'], 10, 2)
            
            # Draw active cursor
            if active_hand_pos:
                pygame.draw.circle(screen, config.CYAN, active_hand_pos, 20, 3)
                
                # Draw click progress for menu states
                if state_manager.current_state_id in (config.GAME_MENU, config.GAME_CREDITS, config.GAME_GUIDE):
                    current_state = state_manager.current_state
                    if current_state.click_timer > 0:
                        progress = min(current_state.click_timer / config.CLICK_HOLD_TIME, 1.0)
                        draw_progress_circle(screen, active_hand_pos, 20, progress, config.GREEN)
        
        # Handle game over transition
        if state_manager.current_state_id == config.GAME_OVER:
            game_over_state = states[config.GAME_OVER]
            if game_over_state.play_duration == 0:
                gameplay_state = states[config.GAME_PLAY]
                game_over_state.set_play_duration(gameplay_state.get_play_duration())
        
        # Update display
        pygame.display.flip()
    
    # Cleanup
    camera.release()
    sound_manager.cleanup()
    game_engine.cleanup()
    state_manager.cleanup()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
