"""
Game State Manager
Handles state transitions and state-specific logic.
"""
import config


class GameStateManager:
    """Manages game states and transitions."""
    
    def __init__(self, screen, sound_manager):
        """
        Initialize game state manager.
        
        Args:
            screen: Pygame screen surface
            sound_manager: Sound manager instance
        """
        self.screen = screen
        self.sound_manager = sound_manager
        self.current_state_id = config.GAME_MENU
        
        # Will be initialized after imports are available
        self.states = {}
        self.current_state = None
    
    def initialize_states(self, state_dict):
        """
        Initialize all game states.
        
        Args:
            state_dict: Dictionary mapping state IDs to state instances
        """
        self.states = state_dict
        self.current_state = self.states[self.current_state_id]
        self.current_state.on_enter()
    
    def change_state(self, new_state_id):
        """
        Change to a new state.
        
        Args:
            new_state_id: ID of the new state to transition to
        """
        if new_state_id is None or new_state_id == self.current_state_id:
            return
        
        if new_state_id in self.states:
            # Exit current state
            if self.current_state:
                self.current_state.on_exit()
            
            # Change state
            self.current_state_id = new_state_id
            self.current_state = self.states[new_state_id]
            
            # Enter new state
            self.current_state.on_enter()
    
    def update(self, dt, landmarks, hand_info):
        """
        Update current state.
        
        Args:
            dt: Delta time in seconds
            landmarks: Pose landmarks from MediaPipe
            hand_info: Hand detection info dict
        """
        if self.current_state:
            next_state = self.current_state.update(dt, landmarks, hand_info)
            
            if next_state is not None:
                self.change_state(next_state)
    
    def render(self):
        """Render current state."""
        if self.current_state:
            self.current_state.render()
    
    def handle_event(self, event):
        """
        Handle pygame events.
        
        Args:
            event: Pygame event
        """
        if self.current_state:
            next_state = self.current_state.handle_event(event)
            
            if next_state is not None:
                self.change_state(next_state)
    
    def cleanup(self):
        """Cleanup all states."""
        if self.current_state:
            self.current_state.on_exit()
