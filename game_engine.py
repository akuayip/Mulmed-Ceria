"""
Game Engine Module
Main game loop and logic for Cam-Fu.
"""

import pygame
import cv2
import numpy as np
import random
from pose_detector import PoseDetector
from collision_detector import CollisionDetector
from game_objects import Target, Obstacle, PowerUp
from score_manager import ScoreManager
from sound_manager import SoundManager
import mediapipe as mp

# Impor kelas baru kita
from renderer import GameRenderer
from spawn_manager import SpawnManager


class GameEngine:
    """
    Main game engine that handles game loop, rendering, and logic.
    """

    def __init__(self, screen_width=1280, screen_height=720, camera_id=0):
        """
        Initialize Game Engine.
        """
        # Initialize Pygame
        pygame.init()
        
        # Screen setup
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Cam-Fu - Pose Fighting Game")
        
        # Game components 
        self.camera_id = camera_id
        self.cap = None
        self.pose_detector = None
        self.collision_detector = CollisionDetector(collision_radius=25)
        self.score_manager = ScoreManager(starting_lives=3)
        self.sound_manager = SoundManager()
        
        # Inisialisasi manajer baru
        self.renderer = GameRenderer(self.screen)
        self.spawn_manager = SpawnManager(self.screen_width, self.screen_height)
        
        # Game objects
        self.targets = []
        self.obstacles = []
        self.powerups = []
        
        # Game state
        self.running = True
        self.paused = False
        self.show_camera = True 
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # MediaPipe pose landmarks
        self.mp_pose = mp.solutions.pose.PoseLandmark
        
        # Hand tracking state
        self.hand_info = {
            'left_hand': {'position': None, 'is_fist': False},
            'right_hand': {'position': None, 'is_fist': False}
        }

    def initialize(self):
        """Initialize camera and pose detector."""
        print("Initializing camera...")
        self.cap = cv2.VideoCapture(self.camera_id)
        
        if not self.cap.isOpened():
            print(f"Error: Could not open camera {self.camera_id}")
            return False
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("Initializing pose detector with hand tracking...")
        self.pose_detector = PoseDetector(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        print("Initialization complete!")
        return True

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r and self.score_manager.game_over:
                    self.reset_game()
                elif event.key == pygame.K_c:
                    self.show_camera = not self.show_camera

    def reset_game(self):
        """Reset game state."""
        self.score_manager.reset()
        self.targets.clear()
        self.obstacles.clear()
        self.powerups.clear()
        self.spawn_manager.reset_timers() 

    def update(self, dt: float, landmarks, hand_info):
        """
        Update game logic.
        
        Args:
            dt: Delta time in seconds
            landmarks: Body pose landmarks
            hand_info: Hand tracking information with fist status
        """
        if self.paused or self.score_manager.game_over:
            return

        # Store hand info for rendering
        self.hand_info = hand_info

        # Apply slow motion if active
        if self.score_manager.slow_motion_active:
            dt *= 0.5

        # Update score manager
        self.score_manager.update(dt)

        # Update spawn timers and spawn objects 
        self.spawn_manager.update(dt, self.targets, self.obstacles, self.powerups)

        # Update all game objects
        for target in self.targets[:]:
            target.update(dt)

        for obstacle in self.obstacles[:]:
            obstacle.update(dt)

        for powerup in self.powerups[:]:
            powerup.update(dt)
            if not powerup.active:
                self.powerups.remove(powerup)

        # Check collisions if pose detected
        if landmarks:
            self.check_collisions(landmarks, hand_info)

        # Remove inactive objects
        self.targets = [t for t in self.targets if t.active]
        self.obstacles = [o for o in self.obstacles if o.active]


    def check_collisions(self, landmarks, hand_info):
        """
        Check collisions between pose/hands and game objects.
        
        Args:
            landmarks: Body pose landmarks
            hand_info: Hand tracking information with fist status
        """
        # Extract hand positions and fist status
        left_hand_pos = hand_info['left_hand']['position']
        right_hand_pos = hand_info['right_hand']['position']
        left_is_fist = hand_info['left_hand']['is_fist']
        right_is_fist = hand_info['right_hand']['is_fist']

        # Check target collisions (REQUIRES FIST to punch!)
        for target in self.targets[:]:
            if not target.active: 
                continue
            
            collision_hand = self.collision_detector.check_hand_collision(
                left_hand_pos, right_hand_pos,
                left_is_fist, right_is_fist,
                target.get_position(), target.radius,
                require_fist=True  # Must be fist to punch targets!
            )
            
            if collision_hand:  # Returns 'left', 'right', or ''
                target.active = False
                self.score_manager.add_score(target.points)
                self.score_manager.targets_hit += 1
                self.sound_manager.play_sound('hit')

        # Check powerup collisions (NO FIST REQUIRED - open hand can grab)
        for powerup in self.powerups[:]:
            if not powerup.active: 
                continue
            
            collision_hand = self.collision_detector.check_hand_collision(
                left_hand_pos, right_hand_pos,
                left_is_fist, right_is_fist,
                powerup.get_position(), powerup.radius,
                require_fist=False  # Open hand can grab powerups
            )
            
            if collision_hand:
                powerup.active = False
                self.score_manager.activate_powerup(powerup.type)
                self.sound_manager.play_sound('powerup')

        # Check obstacle collisions (body collision, not hand)
        body_points = [
            self.pose_detector.get_landmark_position(
                landmarks, self.mp_pose.NOSE.value,
                self.screen_width, self.screen_height
            ),
        ]

        for obstacle in self.obstacles[:]:
            if not obstacle.active: 
                continue
            
            if self.collision_detector.check_body_collision(
                body_points, obstacle.get_position(), obstacle.radius
            ):
                obstacle.active = False
                if self.score_manager.lose_life():
                    self.score_manager.subtract_score(obstacle.damage)
                    self.sound_manager.play_sound('damage')


    def run(self):
        """Main game loop."""
        if not self.initialize():
            return

        print("\n" + "=" * 50)
        print("CAM-FU - Pose Fighting Game")
        print("=" * 50 + "\n")

        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0 

            # Handle events
            self.handle_events()

            # Capture frame
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to capture frame")
                break
            
            frame = cv2.flip(frame, 1)

            # Detect pose
            frame_rgb, landmarks = self.pose_detector.detect_pose(frame)
            
            # Detect hands and get fist status
            hand_info = self.pose_detector.get_hand_info(
                frame_rgb, 
                self.screen_width, 
                self.screen_height
            )

            # Update game logic
            self.update(dt, landmarks, hand_info)
            
            # 1. Clear screen
            self.renderer.clear_screen()

            # 2. Draw all game objects
            self.renderer.draw_game_objects(self.targets, self.obstacles, self.powerups)

            # 3. Draw stickman overlay
            if landmarks:
                self.renderer.draw_stickman(landmarks, self.pose_detector) 
            
            # 4. Draw hand landmarks and fist indicators
            self.renderer.draw_hand_indicators(hand_info)

            # 5. Draw UI elements
            self.renderer.draw_ui(self.score_manager, self.clock, hand_info)

            # 6. Update display
            pygame.display.flip()

        # Cleanup
        self.cleanup()

    def cleanup(self):
        """Clean up resources."""
        print("\nCleaning up...")
        if self.cap:
            self.cap.release()
        if self.pose_detector:
            self.pose_detector.close()
        self.sound_manager.cleanup()
        pygame.quit()
        print("Cleanup complete!")
