"""
Camera Manager
Handles webcam operations.
"""
import cv2


class CameraManager:
    """Manages webcam capture and frame processing."""
    
    def __init__(self, camera_id=0):
        """
        Initialize camera manager.
        
        Args:
            camera_id: Camera device ID (default 0)
        """
        self.camera_id = camera_id
        self.cap = cv2.VideoCapture(camera_id)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera {camera_id}")
    
    def get_frame(self):
        """
        Get current camera frame (flipped horizontally).
        
        Returns:
            numpy.ndarray or None: BGR frame or None if read failed
        """
        ret, frame = self.cap.read()
        
        if not ret:
            return None
        
        # Flip horizontally (mirror effect)
        frame = cv2.flip(frame, 1)
        return frame
    
    def get_frame_rgb(self):
        """
        Get current camera frame in RGB format.
        
        Returns:
            numpy.ndarray or None: RGB frame or None if read failed
        """
        frame = self.get_frame()
        
        if frame is None:
            return None
        
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    def get_frame_size(self):
        """
        Get frame dimensions.
        
        Returns:
            tuple: (width, height) or None if camera not opened
        """
        if not self.cap.isOpened():
            return None
        
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (width, height)
    
    def release(self):
        """Release camera resources."""
        if self.cap:
            self.cap.release()
    
    def is_opened(self):
        """Check if camera is opened."""
        return self.cap.isOpened()
