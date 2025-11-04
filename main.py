"""
Real-time Stickman Pose Detection
Main application that captures webcam input and displays pose as stickman.
"""

import cv2
import sys
import numpy as np
from pose_detector import PoseDetector
from stickman_renderer import StickmanRenderer


class StickmanApp:
    """
    Main application class for real-time stickman pose detection.
    """

    def __init__(self, camera_id=1):
        """
        Initialize the Stickman Application.

        Args:
            camera_id: ID of the camera to use (default: 0)
                      0 = Default/Built-in camera
                      1 = External camera 1
                      2 = External camera 2, dst.
        """
        self.camera_id = camera_id
        self.cap = None
        self.pose_detector = None
        self.renderer = None
        self.is_running = False

    def initialize(self):
        """
        Initialize camera and components.

        Returns:
            bool: True if successful, False otherwise
        """
        print(f"Initializing camera {self.camera_id}...")
        self.cap = cv2.VideoCapture(self.camera_id)
        
        if not self.cap.isOpened():
            print(f"Error: Could not open camera {self.camera_id}")
            return False

        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        print("Initializing pose detector...")
        self.pose_detector = PoseDetector(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        print("Initializing stickman renderer...")
        self.renderer = StickmanRenderer(
            line_color=(0, 255, 0),      # Green lines
            joint_color=(255, 255, 255),  # White joints
            line_thickness=3,
            joint_radius=5
        )

        print("Initialization complete!")
        return True

    def process_frame(self, frame):
        """
        Process a single frame.

        Args:
            frame: Input frame from camera

        Returns:
            tuple: (stickman_canvas, original_frame, landmarks)
                - stickman_canvas: Black canvas with stickman
                - original_frame: Original camera frame
                - landmarks: Detected landmarks
        """
        # Detect pose
        _, landmarks = self.pose_detector.detect_pose(frame)

        # Create black canvas for stickman
        stickman_canvas = self.renderer.create_black_canvas(
            frame.shape[1],
            frame.shape[0]
        )

        # Draw stickman on black canvas
        stickman_canvas = self.renderer.draw_stickman(
            stickman_canvas,
            landmarks,
            self.pose_detector
        )

        # Add status text to stickman canvas
        status = "Person Detected" if landmarks else "No Person Detected"
        stickman_canvas = self.renderer.add_info_text(stickman_canvas, status)

        # Add label to stickman canvas
        stickman_canvas = self.renderer.add_info_text(
            stickman_canvas,
            "STICKMAN VIEW",
            position=(10, 60)
        )

        # Add instructions to stickman canvas
        stickman_canvas = self.renderer.add_info_text(
            stickman_canvas,
            "Press 'q' to quit",
            position=(10, stickman_canvas.shape[0] - 10)
        )

        # Add label to original frame
        original_frame = frame.copy()
        cv2.putText(
            original_frame,
            "CAMERA VIEW",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        return stickman_canvas, original_frame, landmarks

    def run(self):
        """
        Main application loop.
        """
        if not self.initialize():
            return

        self.is_running = True
        print("\nStarting stickman detection...")
        print("Press 'q' to quit\n")

        # Create single window for combined view
        cv2.namedWindow('Stickman Pose Detection - Split View', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Stickman Pose Detection - Split View', 1280, 480)

        try:
            while self.is_running:
                # Capture frame
                ret, frame = self.cap.read()
                
                if not ret:
                    print("Error: Failed to capture frame")
                    break

                # Process frame - get both stickman and original
                stickman_frame, original_frame, landmarks = self.process_frame(frame)

                # Combine both frames horizontally (side by side)
                # Stickman di kiri, Camera asli di kanan
                combined_frame = np.hstack((stickman_frame, original_frame))

                # Add separator line in the middle
                height = combined_frame.shape[0]
                mid_x = combined_frame.shape[1] // 2
                cv2.line(combined_frame, (mid_x, 0), (mid_x, height), (255, 255, 255), 2)

                # Display combined frame
                cv2.imshow('Stickman Pose Detection - Split View', combined_frame)

                # Check for quit command
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    print("\nQuitting...")
                    break

        except KeyboardInterrupt:
            print("\nInterrupted by user")
        finally:
            self.cleanup()

    def cleanup(self):
        """
        Release resources and cleanup.
        """
        print("Cleaning up...")
        self.is_running = False
        
        if self.cap is not None:
            self.cap.release()
        
        if self.pose_detector is not None:
            self.pose_detector.close()
        
        cv2.destroyAllWindows()
        print("Cleanup complete")


def main():
    """
    Entry point of the application.
    """
    print("=" * 50)
    print("Real-time Stickman Pose Detection")
    print("=" * 50)
    
    # ============================================================
    # CARA MENGGANTI CAMERA:
    # Ubah angka di camera_id= untuk memilih camera yang berbeda
    # 
    # camera_id=0  -> Camera default/built-in (biasanya webcam laptop)
    # camera_id=1  -> External camera pertama
    # camera_id=2  -> External camera kedua
    # dst...
    # ============================================================
    
    app = StickmanApp(camera_id=0)  # <-- GANTI ANGKA DI SINI
    app.run()
    
    print("\nApplication terminated successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
