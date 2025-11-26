"""Utility functions used across the game."""
import pygame
from typing import Optional, Tuple, Dict, Any


def is_same_position(pos1: Optional[Tuple[int, int]], pos2: Optional[Tuple[int, int]], threshold: int = 80) -> bool:
    """Check if two positions are within threshold distance."""
    if pos1 is None or pos2 is None:
        return False
    return abs(pos1[0] - pos2[0]) < threshold and abs(pos1[1] - pos2[1]) < threshold


def stable_hover(current_pos: Optional[Tuple[int, int]], prev_pos: Optional[Tuple[int, int]], threshold: int = 80) -> bool:
    """Check if position is stable (not moving much)."""
    if current_pos is None:
        return False
    if prev_pos is None:
        return True
    return is_same_position(current_pos, prev_pos, threshold)


def get_active_hand_position(hand_info: Dict[str, Dict[str, Any]]) -> Optional[Tuple[int, int]]:
    """Get active hand position from hand info."""
    if hand_info.get('right_hand', {}).get('position'):
        return hand_info['right_hand']['position']
    elif hand_info.get('left_hand', {}).get('position'):
        return hand_info['left_hand']['position']
    return None


def draw_progress_circle(screen: pygame.Surface, center: Tuple[int, int], radius: int, progress: float, color: Tuple[int, int, int], thickness: int = 3) -> None:
    """Draw circular progress indicator."""
    if progress > 0:
        progress_radius = int(radius * progress)
        pygame.draw.circle(screen, color, center, progress_radius)
