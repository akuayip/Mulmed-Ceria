"""
"""Stickman renderer - draws pose landmarks as stickman figure."""
import pygame
import mediapipe as mp
from typing import Optional, Tuple, Any


class StickmanRenderer:
    """Renders pose landmarks as white stickman figure."""
    
    def __init__(self, screen: pygame.Surface) -> None:
        """Initialize stickman renderer with screen."""
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Appearance settings
        self.body_color = (255, 255, 255)  # White
        self.line_thickness = 65
        self.joint_radius = self.line_thickness // 2
        
        # MediaPipe pose landmarks
        self.mp_pose = mp.solutions.pose.PoseLandmark
    
    def update_screen_size(self, width: int, height: int) -> None:
        """Update screen dimensions."""
        self.screen_width = width
        self.screen_height = height
    
    def draw(self, landmarks: Any, pose_detector: Any) -> None:
        """Draw stickman from pose landmarks."""
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
    
    def _calculate_midpoint(self, point1: Optional[Tuple[int, int]], point2: Optional[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """Calculate midpoint between two points."""
        if point1 and point2:
            return ((point1[0] + point2[0]) // 2, (point1[1] + point2[1]) // 2)
        return None
    
    def _calculate_head_position(self, nose: Optional[Tuple[int, int]], left_ear: Optional[Tuple[int, int]], right_ear: Optional[Tuple[int, int]]) -> Tuple[Optional[Tuple[int, int]], int]:
        """Calculate head center and radius from nose and ear positions."""
        if not nose:
            return None, 30
        
        head_radius = 30
        if left_ear and right_ear:
            ear_distance = abs(left_ear[0] - right_ear[0])
            head_radius = int(ear_distance * 0.75)
        
        return nose, head_radius
    
    def _draw_torso(self, neck_point: Optional[Tuple[int, int]], pelvis_point: Optional[Tuple[int, int]]) -> None:
        """Draw torso line from neck to pelvis."""
        if neck_point and pelvis_point:
            pygame.draw.line(self.screen, self.body_color, neck_point, pelvis_point, self.line_thickness)
    
    def _draw_neck(self, head_center: Optional[Tuple[int, int]], neck_point: Optional[Tuple[int, int]]) -> None:
        """Draw neck line from head to shoulders."""
        if head_center and neck_point:
            pygame.draw.line(self.screen, self.body_color, head_center, neck_point, self.line_thickness)
    
    def _draw_arms(self, neck_point: Optional[Tuple[int, int]], left_elbow: Optional[Tuple[int, int]], left_wrist: Optional[Tuple[int, int]], right_elbow: Optional[Tuple[int, int]], right_wrist: Optional[Tuple[int, int]]) -> None:
        """Draw both arms (upper and lower)."""
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
    
    def _draw_legs(self, pelvis_point: Optional[Tuple[int, int]], left_knee: Optional[Tuple[int, int]], left_ankle: Optional[Tuple[int, int]], right_knee: Optional[Tuple[int, int]], right_ankle: Optional[Tuple[int, int]]) -> None:
        """Draw both legs (upper and lower)."""
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
    
    def _draw_joints(self, neck_point: Optional[Tuple[int, int]], pelvis_point: Optional[Tuple[int, int]], left_elbow: Optional[Tuple[int, int]], right_elbow: Optional[Tuple[int, int]], left_knee: Optional[Tuple[int, int]], right_knee: Optional[Tuple[int, int]], left_wrist: Optional[Tuple[int, int]], right_wrist: Optional[Tuple[int, int]], left_ankle: Optional[Tuple[int, int]], right_ankle: Optional[Tuple[int, int]]) -> None:
        """Draw circles at all joint positions."""
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
    
    def _draw_head(self, head_center: Optional[Tuple[int, int]], head_radius: int) -> None:
        """Draw head as circle."""
        if head_center:
            pygame.draw.circle(self.screen, self.body_color, head_center, head_radius)
