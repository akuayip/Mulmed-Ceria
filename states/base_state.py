"""Abstract base class for all game states."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import pygame


class BaseState(ABC):
    """Abstract base class for game states."""
    
    def __init__(self, screen: pygame.Surface, sound_manager: Any) -> None:
        """Initialize base state."""
        self.screen = screen
        self.sound_manager = sound_manager
    
    @abstractmethod
    def on_enter(self) -> None:
        """Called when entering this state."""
        pass
    
    @abstractmethod
    def on_exit(self) -> None:
        """Called when exiting this state."""
        pass
    
    @abstractmethod
    def update(self, dt: float, landmarks: Any, hand_info: Dict[str, Dict[str, Any]]) -> Optional[int]:
        """Update state logic, return next state ID or None."""
        pass
    
    @abstractmethod
    def render(self) -> None:
        """Render state visuals."""
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> Optional[int]:
        """Handle pygame events, return next state ID or None."""
        pass
