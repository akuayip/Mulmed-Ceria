"""
Game Renderer Module
Handles all drawing operations for the Cam-Fu game.
"""

import pygame
import mediapipe as mp

class GameRenderer:
    """
    Handles all rendering tasks, including UI, stickman, and objects.
    """

    def __init__(self, screen):
        """
        Initialize the renderer.
        Args:
            screen: The main pygame.Surface to draw on.
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
    
    def update_screen_size(self, new_w, new_h):
        self.screen_width = new_w
        self.screen_height = new_h
        
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

    def clear_screen(self):
        """Fills the screen with black."""
        self.screen.fill(self.BLACK)

    def draw_game_objects(self, targets, obstacles, powerups):
        """Draw all active game objects."""
        for target in targets:
            target.draw(self.screen)
            
        for obstacle in obstacles:
            obstacle.draw(self.screen)
            
        for powerup in powerups:
            powerup.draw(self.screen)

    def draw_ui(self, score_manager, clock):
        """Draw UI elements (score, lives, etc.)."""
        # Draw FPS (top left corner)
        fps = int(clock.get_fps())
        fps_text = self.font_small.render(f"FPS: {fps}", True, self.GREEN)
        self.screen.blit(fps_text, (self.screen_width - 100, 20))
        
        # Draw score
        score_text = self.font_medium.render(f"SCORE: {score_manager.score}", True, self.WHITE)
        self.screen.blit(score_text, (20, 20))

        # Draw lives (hearts)
        for i in range(score_manager.lives):
            pygame.draw.circle(self.screen, self.RED, (20 + i * 40, 70), 15)

        # Draw active power-ups
        y_offset = 110
        if score_manager.shield_active:
            shield_text = self.font_small.render(
                f"SHIELD: {int(score_manager.shield_duration)}s", True, self.BLUE
            )
            self.screen.blit(shield_text, (20, y_offset))
            y_offset += 30

        if score_manager.double_score_active:
            double_text = self.font_small.render(
                f"2X SCORE: {int(score_manager.double_score_duration)}s", True, self.YELLOW
            )
            self.screen.blit(double_text, (20, y_offset))
            y_offset += 30

        if score_manager.slow_motion_active:
            slow_text = self.font_small.render(
                f"SLOW-MO: {int(score_manager.slow_motion_duration)}s", True, self.GREEN
            )
            self.screen.blit(slow_text, (20, y_offset))

        # Draw instructions
        inst_text = self.font_small.render(
            "PUNCH targets (green) | DODGE obstacles (red) | GRAB powerups (yellow)",
            True, self.WHITE
        )
        self.screen.blit(inst_text, (20, self.screen_height - 30))

        # Game over screen
        if score_manager.game_over:
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.set_alpha(200)
            overlay.fill(self.BLACK)
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.font_large.render("GAME OVER", True, self.RED)
            final_score_text = self.font_medium.render(
                f"Final Score: {score_manager.score}", True, self.WHITE
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


    def draw_stickman(self, landmarks, pose_detector):
        """
        Draw stickman overlay on game screen.
        Args:
            landmarks: Pose landmarks
            pose_detector: The PoseDetector instance (to use its get_landmark_position)
        """
        if not landmarks:
            return

        BODY_COLOR = self.WHITE 
        LINE_THICKNESS = 65       
        JOINT_RADIUS = LINE_THICKNESS // 2

        nose = pose_detector.get_landmark_position(landmarks, self.mp_pose.NOSE.value, self.screen_width, self.screen_height)
        left_ear = pose_detector.get_landmark_position(landmarks, self.mp_pose.LEFT_EAR.value, self.screen_width, self.screen_height)
        right_ear = pose_detector.get_landmark_position(landmarks, self.mp_pose.RIGHT_EAR.value, self.screen_width, self.screen_height)
        
        left_shoulder = pose_detector.get_landmark_position(landmarks, self.mp_pose.LEFT_SHOULDER.value, self.screen_width, self.screen_height)
        right_shoulder = pose_detector.get_landmark_position(landmarks, self.mp_pose.RIGHT_SHOULDER.value, self.screen_width, self.screen_height)
        left_hip = pose_detector.get_landmark_position(landmarks, self.mp_pose.LEFT_HIP.value, self.screen_width, self.screen_height)
        right_hip = pose_detector.get_landmark_position(landmarks, self.mp_pose.RIGHT_HIP.value, self.screen_width, self.screen_height)
        
        left_elbow = pose_detector.get_landmark_position(landmarks, self.mp_pose.LEFT_ELBOW.value, self.screen_width, self.screen_height)
        left_wrist = pose_detector.get_landmark_position(landmarks, self.mp_pose.LEFT_WRIST.value, self.screen_width, self.screen_height)
        right_elbow = pose_detector.get_landmark_position(landmarks, self.mp_pose.RIGHT_ELBOW.value, self.screen_width, self.screen_height)
        right_wrist = pose_detector.get_landmark_position(landmarks, self.mp_pose.RIGHT_WRIST.value, self.screen_width, self.screen_height)
        
        left_knee = pose_detector.get_landmark_position(landmarks, self.mp_pose.LEFT_KNEE.value, self.screen_width, self.screen_height)
        left_ankle = pose_detector.get_landmark_position(landmarks, self.mp_pose.LEFT_ANKLE.value, self.screen_width, self.screen_height)
        right_knee = pose_detector.get_landmark_position(landmarks, self.mp_pose.RIGHT_KNEE.value, self.screen_width, self.screen_height)
        right_ankle = pose_detector.get_landmark_position(landmarks, self.mp_pose.RIGHT_ANKLE.value, self.screen_width, self.screen_height)
        

        neck_point = None
        pelvis_point = None

        if left_shoulder and right_shoulder:
            neck_point = (
                (left_shoulder[0] + right_shoulder[0]) // 2,
                (left_shoulder[1] + right_shoulder[1]) // 2
            )

        if left_hip and right_hip:
            pelvis_point = (
                (left_hip[0] + right_hip[0]) // 2,
                (left_hip[1] + right_hip[1]) // 2
            )

        head_center = None
        head_radius = 30 

        if nose:
            head_center_x_calc = nose[0]
            head_center_y_calc = nose[1] 
            
            if left_ear and right_ear:
                ear_distance = abs(left_ear[0] - right_ear[0])
                head_radius = int(ear_distance * 0.75)
            
            head_center_y_calc = nose[1] 
            head_center = (head_center_x_calc, head_center_y_calc)
            pygame.draw.circle(self.screen, BODY_COLOR, head_center, head_radius) 


        if neck_point and pelvis_point:
            pygame.draw.line(self.screen, BODY_COLOR, neck_point, pelvis_point, LINE_THICKNESS)
            
            if head_center:
                pygame.draw.line(self.screen, BODY_COLOR, head_center, neck_point, LINE_THICKNESS)

        if neck_point:
            if left_elbow:
                pygame.draw.line(self.screen, BODY_COLOR, neck_point, left_elbow, LINE_THICKNESS)
                if left_wrist:
                    pygame.draw.line(self.screen, BODY_COLOR, left_elbow, left_wrist, LINE_THICKNESS)
            
            if right_elbow:
                pygame.draw.line(self.screen, BODY_COLOR, neck_point, right_elbow, LINE_THICKNESS)
                if right_wrist:
                    pygame.draw.line(self.screen, BODY_COLOR, right_elbow, right_wrist, LINE_THICKNESS)

        if pelvis_point:
            if left_knee:
                pygame.draw.line(self.screen, BODY_COLOR, pelvis_point, left_knee, LINE_THICKNESS)
                if left_ankle:
                    pygame.draw.line(self.screen, BODY_COLOR, left_knee, left_ankle, LINE_THICKNESS)
            
            if right_knee:
                pygame.draw.line(self.screen, BODY_COLOR, pelvis_point, right_knee, LINE_THICKNESS)
                if right_ankle:
                    pygame.draw.line(self.screen, BODY_COLOR, right_knee, right_ankle, LINE_THICKNESS)
                            
        all_joints = [
            neck_point,    
            pelvis_point,   
            left_elbow,
            right_elbow,
            left_knee,
            right_knee,
            left_wrist,     
            right_wrist,
            left_ankle,     
            right_ankle
        ]

        for joint in all_joints:
            if joint:
                pygame.draw.circle(self.screen, BODY_COLOR, joint, JOINT_RADIUS)
        
        if head_center:
            pygame.draw.circle(self.screen, BODY_COLOR, head_center, head_radius)