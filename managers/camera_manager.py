"""
Camera Manager Module

This module contains the CameraManager class which handles webcam operations
including frame capture, format conversion, and resource management.
"""
import cv2
import numpy as np
from typing import Optional, Tuple


class CameraManager:
    """
    Manages webcam capture and frame processing.
    
    This class handles:
    - Opening and closing webcam connection
    - Capturing frames in BGR and RGB formats
    - Horizontal flipping for mirror effect
    - Frame dimension queries
    
    Attributes:
        camera_id: Index of the camera device to use
        cap: OpenCV VideoCapture object for camera access
    """
    
    def __init__(self, camera_id: int = 0) -> None:
        """Open webcam connection (raises RuntimeError if camera unavailable)."""
        self.camera_id: int = camera_id
        self.cap: cv2.VideoCapture = cv2.VideoCapture(camera_id)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera {camera_id}")
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get BGR frame with horizontal flip (mirror effect)."""
        ret, frame = self.cap.read()
        
        if not ret:
            return None
        
        # Flip horizontally (mirror effect)
        frame = cv2.flip(frame, 1)
        return frame
    
    def get_frame_rgb(self) -> Optional[np.ndarray]:
        """Get RGB frame (for MediaPipe processing)."""
        frame = self.get_frame()
        
        if frame is None:
            return None
        
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    def get_frame_size(self) -> Optional[Tuple[int, int]]:
        """Get frame dimensions (width, height)."""
        if not self.cap.isOpened():
            return None
        
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (width, height)
    
    def release(self) -> None:
        """Release camera resources."""
        if self.cap:
            self.cap.release()
    
    def is_opened(self) -> bool:
        """Check if camera is currently open."""
        return self.cap.isOpened()
