"""
Pose Detector Module
Handles human pose detection using MediaPipe.
"""

import mediapipe as mp
import cv2


class PoseDetector:
    """
    A class to detect human pose using MediaPipe Pose solution.
    """

    def __init__(
        self,
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ):
        """
        Initialize the PoseDetector.

        Args:
            static_image_mode: Whether to treat input as static images
            model_complexity: Complexity of pose model (0, 1, or 2)
            smooth_landmarks: Whether to smooth landmarks across frames
            min_detection_confidence: Minimum confidence for detection
            min_tracking_confidence: Minimum confidence for tracking
        """
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            smooth_landmarks=smooth_landmarks,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def detect_pose(self, frame):
        """
        Detect pose landmarks in the given frame.

        Args:
            frame: Input BGR image from camera

        Returns:
            tuple: (processed_frame, landmarks)
                - processed_frame: RGB frame after processing
                - landmarks: Detected pose landmarks or None
        """
        # Convert BGR to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.pose.process(frame_rgb)
        
        return frame_rgb, results.pose_landmarks

    def get_landmark_position(self, landmarks, landmark_id, frame_width, frame_height):
        """
        Get the pixel position of a specific landmark.

        Args:
            landmarks: Pose landmarks object
            landmark_id: ID of the landmark to retrieve
            frame_width: Width of the frame
            frame_height: Height of the frame

        Returns:
            tuple: (x, y) pixel coordinates or None
        """
        if landmarks and len(landmarks.landmark) > landmark_id:
            landmark = landmarks.landmark[landmark_id]
            x = int(landmark.x * frame_width)
            y = int(landmark.y * frame_height)
            return (x, y)
        return None

    def close(self):
        """Release resources."""
        self.pose.close()
