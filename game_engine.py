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


class GameEngine:
    """
    Main game engine that handles game loop, rendering, and logic.
    """

    def __init__(self, screen_width=1280, screen_height=720, camera_id=0):
        """
        Initialize Game Engine.

        Args:
            screen_width: Width of game window
            screen_height: Height of game window
            camera_id: Camera device ID
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
        
        # Timers for spawning
        self.target_spawn_timer = 0
        self.target_spawn_interval = 3.0  # Spawn target every 3 seconds
        self.obstacle_spawn_timer = 0
        self.obstacle_spawn_interval = 5.0  # Spawn obstacle every 5 seconds
        self.powerup_spawn_timer = 0
        self.powerup_spawn_interval = 15.0  # Spawn powerup every 15 seconds
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.BLUE = (0, 150, 255)
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # MediaPipe pose landmarks
        self.mp_pose = mp.solutions.pose.PoseLandmark

    def initialize(self):
        """Initialize camera and pose detector."""
        print("Initializing camera...")
        self.cap = cv2.VideoCapture(self.camera_id)
        
        if not self.cap.isOpened():
            print(f"Error: Could not open camera {self.camera_id}")
            return False
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("Initializing pose detector...")
        self.pose_detector = PoseDetector(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        print("Initialization complete!")
        return True

    def spawn_target(self):
        """Spawn a new target."""
        x = random.randint(100, self.screen_width - 100)
        y = random.randint(100, self.screen_height - 100)
        self.targets.append(Target(x, y, self.screen_width, self.screen_height))

    def spawn_obstacle(self):
        """Spawn a new obstacle from random edge."""
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        
        if edge == 'top':
            x = random.randint(0, self.screen_width)
            y = -50
        elif edge == 'bottom':
            x = random.randint(0, self.screen_width)
            y = self.screen_height + 50
        elif edge == 'left':
            x = -50
            y = random.randint(0, self.screen_height)
        else:  # right
            x = self.screen_width + 50
            y = random.randint(0, self.screen_height)
        
        self.obstacles.append(Obstacle(x, y, self.screen_width, self.screen_height))

    def spawn_powerup(self):
        """Spawn a new power-up."""
        x = random.randint(100, self.screen_width - 100)
        y = random.randint(100, self.screen_height - 100)
        self.powerups.append(PowerUp(x, y, self.screen_width, self.screen_height))

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
        self.target_spawn_timer = 0
        self.obstacle_spawn_timer = 0
        self.powerup_spawn_timer = 0

    def update(self, dt: float, landmarks):
        """
        Update game logic.

        Args:
            dt: Delta time
            landmarks: Pose landmarks
        """
        if self.paused or self.score_manager.game_over:
            return

        # Apply slow motion if active
        if self.score_manager.slow_motion_active:
            dt *= 0.5

        # Update score manager
        self.score_manager.update(dt)

        # Update spawn timers
        self.target_spawn_timer += dt
        self.obstacle_spawn_timer += dt
        self.powerup_spawn_timer += dt

        # Spawn objects
        if self.target_spawn_timer >= self.target_spawn_interval:
            self.spawn_target()
            self.target_spawn_timer = 0

        if self.obstacle_spawn_timer >= self.obstacle_spawn_interval:
            self.spawn_obstacle()
            self.obstacle_spawn_timer = 0

        if self.powerup_spawn_timer >= self.powerup_spawn_interval:
            self.spawn_powerup()
            self.powerup_spawn_timer = 0

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
            self.check_collisions(landmarks)

        # Remove inactive objects
        self.targets = [t for t in self.targets if t.active]

    def check_collisions(self, landmarks):
        """
        Check collisions between pose and game objects.

        Args:
            landmarks: Pose landmarks
        """
        # Get hand positions
        left_wrist = self.pose_detector.get_landmark_position(
            landmarks, self.mp_pose.LEFT_WRIST.value,
            self.screen_width, self.screen_height
        )
        right_wrist = self.pose_detector.get_landmark_position(
            landmarks, self.mp_pose.RIGHT_WRIST.value,
            self.screen_width, self.screen_height
        )

        # Check target collisions (hand punch)
        for target in self.targets[:]:
            if not target.active:
                continue
            
            hand_hit = self.collision_detector.check_hand_collision(
                left_wrist, right_wrist,
                target.get_position(), target.radius
            )
            
            if hand_hit:
                target.active = False
                self.score_manager.add_score(target.points)
                self.score_manager.targets_hit += 1
                self.sound_manager.play_sound('hit')

        # Check powerup collisions (hand grab)
        for powerup in self.powerups[:]:
            if not powerup.active:
                continue
            
            hand_hit = self.collision_detector.check_hand_collision(
                left_wrist, right_wrist,
                powerup.get_position(), powerup.radius
            )
            
            if hand_hit:
                powerup.active = False
                self.score_manager.activate_powerup(powerup.type)
                self.sound_manager.play_sound('powerup')

        # Check obstacle collisions (body hit)
        body_points = [
            self.pose_detector.get_landmark_position(
                landmarks, self.mp_pose.NOSE.value,
                self.screen_width, self.screen_height
            ),
            self.pose_detector.get_landmark_position(
                landmarks, self.mp_pose.LEFT_SHOULDER.value,
                self.screen_width, self.screen_height
            ),
            self.pose_detector.get_landmark_position(
                landmarks, self.mp_pose.RIGHT_SHOULDER.value,
                self.screen_width, self.screen_height
            ),
            self.pose_detector.get_landmark_position(
                landmarks, self.mp_pose.LEFT_HIP.value,
                self.screen_width, self.screen_height
            ),
            self.pose_detector.get_landmark_position(
                landmarks, self.mp_pose.RIGHT_HIP.value,
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

    def draw_ui(self):
        """Draw UI elements (score, lives, etc.)."""
        # Draw FPS (top left corner)
        fps = int(self.clock.get_fps())
        fps_text = self.font_small.render(f"FPS: {fps}", True, self.GREEN)
        self.screen.blit(fps_text, (self.screen_width - 100, 20))
        
        # Draw score
        score_text = self.font_medium.render(f"SCORE: {self.score_manager.score}", True, self.WHITE)
        self.screen.blit(score_text, (20, 20))

        # Draw lives (hearts)
        for i in range(self.score_manager.lives):
            pygame.draw.circle(self.screen, self.RED, (20 + i * 40, 70), 15)

        # Draw active power-ups
        y_offset = 110
        if self.score_manager.shield_active:
            shield_text = self.font_small.render(
                f"SHIELD: {int(self.score_manager.shield_duration)}s",
                True, self.BLUE
            )
            self.screen.blit(shield_text, (20, y_offset))
            y_offset += 30

        if self.score_manager.double_score_active:
            double_text = self.font_small.render(
                f"2X SCORE: {int(self.score_manager.double_score_duration)}s",
                True, self.YELLOW
            )
            self.screen.blit(double_text, (20, y_offset))
            y_offset += 30

        if self.score_manager.slow_motion_active:
            slow_text = self.font_small.render(
                f"SLOW-MO: {int(self.score_manager.slow_motion_duration)}s",
                True, self.GREEN
            )
            self.screen.blit(slow_text, (20, y_offset))

        # Draw instructions
        inst_text = self.font_small.render(
            "PUNCH targets (green) | DODGE obstacles (red) | GRAB powerups (yellow)",
            True, self.WHITE
        )
        self.screen.blit(inst_text, (20, self.screen_height - 30))

        # Game over screen
        if self.score_manager.game_over:
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.set_alpha(200)
            overlay.fill(self.BLACK)
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.font_large.render("GAME OVER", True, self.RED)
            final_score_text = self.font_medium.render(
                f"Final Score: {self.score_manager.score}", True, self.WHITE
            )
            restart_text = self.font_small.render(
                "Press R to Restart | ESC to Quit", True, self.WHITE
            )

            self.screen.blit(
                game_over_text,
                (self.screen_width // 2 - game_over_text.get_width() // 2, 250)
            )
            self.screen.blit(
                final_score_text,
                (self.screen_width // 2 - final_score_text.get_width() // 2, 320)
            )
            self.screen.blit(
                restart_text,
                (self.screen_width // 2 - restart_text.get_width() // 2, 380)
            )

    def draw_stickman(self, landmarks):
        """
        Draw stickman overlay on game screen.

        Args:
            landmarks: Pose landmarks
        """
        if not landmarks:
            return

        # Define connections
        connections = [
            (self.mp_pose.LEFT_SHOULDER, self.mp_pose.RIGHT_SHOULDER),
            (self.mp_pose.LEFT_SHOULDER, self.mp_pose.LEFT_ELBOW),
            (self.mp_pose.LEFT_ELBOW, self.mp_pose.LEFT_WRIST),
            (self.mp_pose.RIGHT_SHOULDER, self.mp_pose.RIGHT_ELBOW),
            (self.mp_pose.RIGHT_ELBOW, self.mp_pose.RIGHT_WRIST),
            (self.mp_pose.LEFT_SHOULDER, self.mp_pose.LEFT_HIP),
            (self.mp_pose.RIGHT_SHOULDER, self.mp_pose.RIGHT_HIP),
            (self.mp_pose.LEFT_HIP, self.mp_pose.RIGHT_HIP),
            (self.mp_pose.LEFT_HIP, self.mp_pose.LEFT_KNEE),
            (self.mp_pose.LEFT_KNEE, self.mp_pose.LEFT_ANKLE),
            (self.mp_pose.RIGHT_HIP, self.mp_pose.RIGHT_KNEE),
            (self.mp_pose.RIGHT_KNEE, self.mp_pose.RIGHT_ANKLE),
        ]

        # Draw connections
        for connection in connections:
            start = self.pose_detector.get_landmark_position(
                landmarks, connection[0].value,
                self.screen_width, self.screen_height
            )
            end = self.pose_detector.get_landmark_position(
                landmarks, connection[1].value,
                self.screen_width, self.screen_height
            )
            
            if start and end:
                pygame.draw.line(self.screen, self.GREEN, start, end, 3)

        # Draw joints
        for landmark_id in range(33):
            pos = self.pose_detector.get_landmark_position(
                landmarks, landmark_id,
                self.screen_width, self.screen_height
            )
            if pos:
                pygame.draw.circle(self.screen, self.WHITE, pos, 5)

    def run(self):
        """Main game loop."""
        if not self.initialize():
            return

        print("\n" + "=" * 50)
        print("CAM-FU - Pose Fighting Game")
        print("=" * 50)
        print("Controls:")
        print("  - PUNCH green targets for points")
        print("  - DODGE red obstacles (they damage you!)")
        print("  - GRAB yellow power-ups for bonuses")
        print("  - SPACE: Pause/Unpause")
        print("  - C: Toggle camera view")
        print("  - ESC/Q: Quit")
        print("=" * 50 + "\n")

        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0  # Delta time in seconds

            # Handle events
            self.handle_events()

            # Capture frame
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to capture frame")
                break

            # Flip frame horizontally (mirror)
            frame = cv2.flip(frame, 1)

            # Detect pose
            _, landmarks = self.pose_detector.detect_pose(frame)

            # Update game logic
            self.update(dt, landmarks)

            # Clear screen
            self.screen.fill(self.BLACK)

            # Draw game objects
            for target in self.targets:
                target.draw(self.screen)

            for obstacle in self.obstacles:
                obstacle.draw(self.screen)

            for powerup in self.powerups:
                powerup.draw(self.screen)

            # Draw stickman overlay
            if landmarks:
                self.draw_stickman(landmarks)

            # Draw UI
            self.draw_ui()

            # Update display
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
