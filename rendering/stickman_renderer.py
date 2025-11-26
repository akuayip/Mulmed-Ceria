"""
Stickman Renderer
Handles rendering of pose landmarks as stickman.
"""
import pygame
import mediapipe as mp


class StickmanRenderer:
    """Renders pose landmarks as a stickman figure."""
    
    def __init__(self, screen):
        """
        Initialize stickman renderer.
        
        Args:
            screen: Pygame screen surface
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Appearance settings
        self.body_color = (255, 255, 255)  # White
        self.line_thickness = 65
        self.joint_radius = self.line_thickness // 2
        
        # MediaPipe pose landmarks
        self.mp_pose = mp.solutions.pose.PoseLandmark
    
    def update_screen_size(self, width, height):
        """Update screen dimensions."""
        self.screen_width = width
        self.screen_height = height
    
    def draw(self, landmarks, pose_detector):
        """
        Draw stickman from pose landmarks.
        
        Args:
            landmarks: MediaPipe pose landmarks
            pose_detector: PoseDetector instance for coordinate conversion
        """
        if not landmarks:
            return
        
        # Get all required landmarks
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
        
        # Calculate derived points
        neck_point = self._calculate_midpoint(left_shoulder, right_shoulder)
        pelvis_point = self._calculate_midpoint(left_hip, right_hip)
        head_center, head_radius = self._calculate_head_position(nose, left_ear, right_ear)
        
        # Draw body parts in order
        self._draw_torso(neck_point, pelvis_point)
        self._draw_neck(head_center, neck_point)
        self._draw_arms(neck_point, left_elbow, left_wrist, right_elbow, right_wrist)
        self._draw_legs(pelvis_point, left_knee, left_ankle, right_knee, right_ankle)
        self._draw_joints(neck_point, pelvis_point, left_elbow, right_elbow, left_knee, right_knee, left_wrist, right_wrist, left_ankle, right_ankle)
        self._draw_head(head_center, head_radius)
    
    def _calculate_midpoint(self, point1, point2):
        """Calculate midpoint between two points."""
        if point1 and point2:
            return ((point1[0] + point2[0]) // 2, (point1[1] + point2[1]) // 2)
        return None
    
    def _calculate_head_position(self, nose, left_ear, right_ear):
        """Calculate head center and radius."""
        if not nose:
            return None, 30
        
        head_radius = 30
        if left_ear and right_ear:
            ear_distance = abs(left_ear[0] - right_ear[0])
            head_radius = int(ear_distance * 0.75)
        
        return nose, head_radius
    
    def _draw_torso(self, neck_point, pelvis_point):
        """Draw the torso line."""
        if neck_point and pelvis_point:
            pygame.draw.line(self.screen, self.body_color, neck_point, pelvis_point, self.line_thickness)
    
    def _draw_neck(self, head_center, neck_point):
        """Draw the neck line."""
        if head_center and neck_point:
            pygame.draw.line(self.screen, self.body_color, head_center, neck_point, self.line_thickness)
    
    def _draw_arms(self, neck_point, left_elbow, left_wrist, right_elbow, right_wrist):
        """Draw both arms."""
        if neck_point:
            # Left arm
            if left_elbow:
                pygame.draw.line(self.screen, self.body_color, neck_point, left_elbow, self.line_thickness)
                if left_wrist:
                    pygame.draw.line(self.screen, self.body_color, left_elbow, left_wrist, self.line_thickness)
            
            # Right arm
            if right_elbow:
                pygame.draw.line(self.screen, self.body_color, neck_point, right_elbow, self.line_thickness)
                if right_wrist:
                    pygame.draw.line(self.screen, self.body_color, right_elbow, right_wrist, self.line_thickness)
    
    def _draw_legs(self, pelvis_point, left_knee, left_ankle, right_knee, right_ankle):
        """Draw both legs."""
        if pelvis_point:
            # Left leg
            if left_knee:
                pygame.draw.line(self.screen, self.body_color, pelvis_point, left_knee, self.line_thickness)
                if left_ankle:
                    pygame.draw.line(self.screen, self.body_color, left_knee, left_ankle, self.line_thickness)
            
            # Right leg
            if right_knee:
                pygame.draw.line(self.screen, self.body_color, pelvis_point, right_knee, self.line_thickness)
                if right_ankle:
                    pygame.draw.line(self.screen, self.body_color, right_knee, right_ankle, self.line_thickness)
    
    def _draw_joints(self, neck_point, pelvis_point, left_elbow, right_elbow, left_knee, right_knee, left_wrist, right_wrist, left_ankle, right_ankle):
        """Draw all joint circles."""
        all_joints = [
            neck_point, pelvis_point,
            left_elbow, right_elbow,
            left_knee, right_knee,
            left_wrist, right_wrist,
            left_ankle, right_ankle
        ]
        
        for joint in all_joints:
            if joint:
                pygame.draw.circle(self.screen, self.body_color, joint, self.joint_radius)
    
    def _draw_head(self, head_center, head_radius):
        """Draw the head circle."""
        if head_center:
            pygame.draw.circle(self.screen, self.body_color, head_center, head_radius)
