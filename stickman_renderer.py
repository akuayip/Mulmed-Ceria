"""
Stickman Renderer Module
Handles rendering of detected pose as a stickman figure.
"""

import cv2
import numpy as np
import mediapipe as mp


class StickmanRenderer:
    """
    A class to render detected pose as a stickman on a black background.
    """

    def __init__(self, line_color=(0, 255, 0), joint_color=(255, 255, 255), line_thickness=3, joint_radius=5):
        """
        Initialize the StickmanRenderer.

        Args:
            line_color: BGR color for stickman lines (default: green)
            joint_color: BGR color for joints (default: white)
            line_thickness: Thickness of the lines
            joint_radius: Radius of joint circles
        """
        self.line_color = line_color
        self.joint_color = joint_color
        self.line_thickness = line_thickness
        self.joint_radius = joint_radius
        self.mp_pose = mp.solutions.pose.PoseLandmark

        # Define body connections for stickman
        self.connections = [
            # Face
            (self.mp_pose.NOSE, self.mp_pose.LEFT_EYE),
            (self.mp_pose.NOSE, self.mp_pose.RIGHT_EYE),
            (self.mp_pose.LEFT_EYE, self.mp_pose.LEFT_EAR),
            (self.mp_pose.RIGHT_EYE, self.mp_pose.RIGHT_EAR),
            
            # Torso
            (self.mp_pose.LEFT_SHOULDER, self.mp_pose.RIGHT_SHOULDER),
            (self.mp_pose.LEFT_SHOULDER, self.mp_pose.LEFT_HIP),
            (self.mp_pose.RIGHT_SHOULDER, self.mp_pose.RIGHT_HIP),
            (self.mp_pose.LEFT_HIP, self.mp_pose.RIGHT_HIP),
            
            # Left arm
            (self.mp_pose.LEFT_SHOULDER, self.mp_pose.LEFT_ELBOW),
            (self.mp_pose.LEFT_ELBOW, self.mp_pose.LEFT_WRIST),
            (self.mp_pose.LEFT_WRIST, self.mp_pose.LEFT_PINKY),
            (self.mp_pose.LEFT_WRIST, self.mp_pose.LEFT_INDEX),
            (self.mp_pose.LEFT_WRIST, self.mp_pose.LEFT_THUMB),
            
            # Right arm
            (self.mp_pose.RIGHT_SHOULDER, self.mp_pose.RIGHT_ELBOW),
            (self.mp_pose.RIGHT_ELBOW, self.mp_pose.RIGHT_WRIST),
            (self.mp_pose.RIGHT_WRIST, self.mp_pose.RIGHT_PINKY),
            (self.mp_pose.RIGHT_WRIST, self.mp_pose.RIGHT_INDEX),
            (self.mp_pose.RIGHT_WRIST, self.mp_pose.RIGHT_THUMB),
            
            # Left leg
            (self.mp_pose.LEFT_HIP, self.mp_pose.LEFT_KNEE),
            (self.mp_pose.LEFT_KNEE, self.mp_pose.LEFT_ANKLE),
            (self.mp_pose.LEFT_ANKLE, self.mp_pose.LEFT_HEEL),
            (self.mp_pose.LEFT_ANKLE, self.mp_pose.LEFT_FOOT_INDEX),
            
            # Right leg
            (self.mp_pose.RIGHT_HIP, self.mp_pose.RIGHT_KNEE),
            (self.mp_pose.RIGHT_KNEE, self.mp_pose.RIGHT_ANKLE),
            (self.mp_pose.RIGHT_ANKLE, self.mp_pose.RIGHT_HEEL),
            (self.mp_pose.RIGHT_ANKLE, self.mp_pose.RIGHT_FOOT_INDEX),
        ]

    def create_black_canvas(self, width, height):
        """
        Create a black canvas.

        Args:
            width: Canvas width
            height: Canvas height

        Returns:
            numpy.ndarray: Black image
        """
        return np.zeros((height, width, 3), dtype=np.uint8)

    def draw_stickman(self, canvas, landmarks, pose_detector):
        """
        Draw stickman figure on the canvas.

        Args:
            canvas: Black canvas to draw on
            landmarks: Detected pose landmarks
            pose_detector: PoseDetector instance for coordinate conversion

        Returns:
            numpy.ndarray: Canvas with stickman drawn
        """
        if landmarks is None:
            return canvas

        height, width = canvas.shape[:2]
        
        # Draw connections (lines)
        for connection in self.connections:
            start_point = pose_detector.get_landmark_position(
                landmarks, connection[0].value, width, height
            )
            end_point = pose_detector.get_landmark_position(
                landmarks, connection[1].value, width, height
            )

            if start_point and end_point:
                cv2.line(
                    canvas,
                    start_point,
                    end_point,
                    self.line_color,
                    self.line_thickness
                )

        # Draw head circle
        # Calculate center of head based on nose position
        nose = pose_detector.get_landmark_position(
            landmarks, self.mp_pose.NOSE.value, width, height
        )
        left_ear = pose_detector.get_landmark_position(
            landmarks, self.mp_pose.LEFT_EAR.value, width, height
        )
        right_ear = pose_detector.get_landmark_position(
            landmarks, self.mp_pose.RIGHT_EAR.value, width, height
        )
        
        if nose and left_ear and right_ear:
            # Calculate head center (slightly above nose)
            head_center_x = nose[0]
            head_center_y = nose[1] - 10  # Slightly above nose
            head_center = (head_center_x, head_center_y)
            
            # Calculate head radius based on ear distance
            ear_distance = abs(left_ear[0] - right_ear[0])
            head_radius = int(ear_distance * 0.75)  # Radius is about 75% of ear distance
            
            # Draw the head circle
            cv2.circle(
                canvas,
                head_center,
                head_radius,
                self.line_color,
                self.line_thickness
            )

        # Draw joints (circles)
        for landmark_enum in self.mp_pose:
            point = pose_detector.get_landmark_position(
                landmarks, landmark_enum.value, width, height
            )
            if point:
                cv2.circle(
                    canvas,
                    point,
                    self.joint_radius,
                    self.joint_color,
                    -1
                )

        return canvas

    def add_info_text(self, canvas, text, position=(10, 30)):
        """
        Add informational text to the canvas.

        Args:
            canvas: Canvas to draw on
            text: Text to display
            position: Position (x, y) for text

        Returns:
            numpy.ndarray: Canvas with text
        """
        cv2.putText(
            canvas,
            text,
            position,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        return canvas
