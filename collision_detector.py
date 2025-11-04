"""
Collision Detector Module
Handles collision detection between pose landmarks and game objects.
"""

import math
from typing import Tuple, Optional


class CollisionDetector:
    """
    Detects collisions between body parts (hands, body) and game objects.
    """

    def __init__(self, collision_radius=30):
        """
        Initialize CollisionDetector.

        Args:
            collision_radius: Radius for collision detection in pixels
        """
        self.collision_radius = collision_radius

    def point_distance(self, point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
        """
        Calculate Euclidean distance between two points.

        Args:
            point1: (x, y) coordinates of first point
            point2: (x, y) coordinates of second point

        Returns:
            float: Distance between points
        """
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    def check_collision(
        self,
        landmark_pos: Optional[Tuple[int, int]],
        object_pos: Tuple[int, int],
        object_radius: int
    ) -> bool:
        """
        Check if a landmark collides with an object.

        Args:
            landmark_pos: (x, y) position of landmark (can be None)
            object_pos: (x, y) position of object center
            object_radius: Radius of the object

        Returns:
            bool: True if collision detected, False otherwise
        """
        if landmark_pos is None:
            return False

        distance = self.point_distance(landmark_pos, object_pos)
        return distance < (self.collision_radius + object_radius)

    def check_hand_collision(
        self,
        left_hand: Optional[Tuple[int, int]],
        right_hand: Optional[Tuple[int, int]],
        object_pos: Tuple[int, int],
        object_radius: int
    ) -> str:
        """
        Check if either hand collides with an object.

        Args:
            left_hand: Left hand wrist position
            right_hand: Right hand wrist position
            object_pos: Object center position
            object_radius: Object radius

        Returns:
            str: 'left', 'right', or '' (no collision)
        """
        if self.check_collision(left_hand, object_pos, object_radius):
            return 'left'
        elif self.check_collision(right_hand, object_pos, object_radius):
            return 'right'
        return ''

    def check_body_collision(
        self,
        body_points: list,
        object_pos: Tuple[int, int],
        object_radius: int
    ) -> bool:
        """
        Check if any body part collides with an object.

        Args:
            body_points: List of (x, y) body landmark positions
            object_pos: Object center position
            object_radius: Object radius

        Returns:
            bool: True if any body part collides
        """
        for point in body_points:
            if point is not None and self.check_collision(point, object_pos, object_radius):
                return True
        return False
