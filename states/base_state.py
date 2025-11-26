"""
Base State Class
Abstract class for all game states.
"""
from abc import ABC, abstractmethod


class BaseState(ABC):
    """Abstract base class for game states."""
    
    def __init__(self, screen, sound_manager):
        """
        Initialize base state.
        
        Args:
            screen: Pygame screen surface
            sound_manager: Sound manager instance
        """
        self.screen = screen
        self.sound_manager = sound_manager
    
    @abstractmethod
    def on_enter(self):
        """Called when entering this state."""
        pass
    
    @abstractmethod
    def on_exit(self):
        """Called when exiting this state."""
        pass
    
    @abstractmethod
    def update(self, dt, landmarks, hand_info):
        """
        Update state logic.
        
        Args:
            dt: Delta time in seconds
            landmarks: Pose landmarks from MediaPipe
            hand_info: Hand detection info dict
        
        Returns:
            int or None: Next state ID if state should change, None otherwise
        """
        pass
    
    @abstractmethod
    def render(self):
        """Render state visuals."""
        pass
    
    @abstractmethod
    def handle_event(self, event):
        """
        Handle pygame events.
        
        Args:
            event: Pygame event
        
        Returns:
            int or None: Next state ID if event triggers state change
        """
        pass
