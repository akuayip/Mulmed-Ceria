"""
Collision Detector Module
Handles collision detection between pose landmarks and game objects.
"""

import math
from typing import Tuple, Optional


class CollisionDetector:
    """Detects collisions between body parts and game objects."""

    def __init__(self, collision_radius: int = 30) -> None:
        """Initialize collision detector with radius."""
        self.collision_radius = collision_radius

    def point_distance(self, point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
        """Calculate Euclidean distance between two points."""
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    def check_collision(
        self,
        landmark_pos: Optional[Tuple[int, int]],
        object_pos: Tuple[int, int],
        object_radius: int
    ) -> bool:
        """Check if landmark collides with object."""
        if landmark_pos is None:
            return False

        distance = self.point_distance(landmark_pos, object_pos)
        return distance < (self.collision_radius + object_radius)

    def check_hand_collision(
        self,
        left_hand_pos: Optional[Tuple[int, int]],
        right_hand_pos: Optional[Tuple[int, int]],
        left_is_fist: bool,
        right_is_fist: bool,
        object_pos: Tuple[int, int],
        object_radius: int,
        require_fist: bool = False
    ) -> str:
        """Check if any hand collides with object (returns 'left', 'right', or '')."""
        # Check left hand
        if left_hand_pos is not None:
            if self.check_collision(left_hand_pos, object_pos, object_radius):
                # If fist is required, check fist status
                if require_fist:
                    if left_is_fist:
                        return 'left'
                else:
                    # No fist required (e.g., for powerups)
                    return 'left'
        
        # Check right hand
        if right_hand_pos is not None:
            if self.check_collision(right_hand_pos, object_pos, object_radius):
                # If fist is required, check fist status
                if require_fist:
                    if right_is_fist:
                        return 'right'
                else:
                    # No fist required (e.g., for powerups)
                    return 'right'
        
        return ''

    def check_body_collision(
        self,
        body_points: list,
        object_pos: Tuple[int, int],
        object_radius: int
    ) -> bool:
        """Check if any body part collides with object."""
        for point in body_points:
            if point is not None and self.check_collision(point, object_pos, object_radius):
                return True
        return False
