"""
Helper Functions
Utility functions used across the game.
"""
import pygame


def is_same_position(pos1, pos2, threshold=80):
    """
    Check if two positions are within threshold distance.
    
    Args:
        pos1: First position tuple (x, y)
        pos2: Second position tuple (x, y)
        threshold: Maximum distance to consider same
    
    Returns:
        bool: True if positions are within threshold
    """
    if pos1 is None or pos2 is None:
        return False
    return abs(pos1[0] - pos2[0]) < threshold and abs(pos1[1] - pos2[1]) < threshold


def stable_hover(current_pos, prev_pos, threshold=80):
    """
    Check if current position is stable (not moving much).
    
    Args:
        current_pos: Current position tuple (x, y)
        prev_pos: Previous position tuple (x, y)
        threshold: Maximum movement to consider stable
    
    Returns:
        bool: True if position is stable
    """
    if current_pos is None:
        return False
    if prev_pos is None:
        return True
    return is_same_position(current_pos, prev_pos, threshold)


def get_active_hand_position(hand_info):
    """
    Get the active hand position from hand info.
    
    Args:
        hand_info: Hand detection info dictionary
    
    Returns:
        tuple or None: Active hand position (x, y) or None
    """
    if hand_info.get('right_hand', {}).get('position'):
        return hand_info['right_hand']['position']
    elif hand_info.get('left_hand', {}).get('position'):
        return hand_info['left_hand']['position']
    return None


def draw_progress_circle(screen, center, radius, progress, color, thickness=3):
    """
    Draw a circular progress indicator.
    
    Args:
        screen: Pygame screen surface
        center: Center position (x, y)
        radius: Circle radius
        progress: Progress value (0.0 to 1.0)
        color: Circle color
        thickness: Line thickness
    """
    if progress > 0:
        progress_radius = int(radius * progress)
        pygame.draw.circle(screen, color, center, progress_radius)
