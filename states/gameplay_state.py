"""
Gameplay State Module

This module contains the GameplayState class which handles all main gameplay logic
including collision detection, entity updates, and game state management.
"""
import pygame
import time
from typing import Optional, Dict, Any
from states.base_state import BaseState
from managers.spawn_manager import SpawnManager
from managers.score_manager import ScoreManager
from detection.collision_detector import CollisionDetector
import config


class GameplayState(BaseState):
    """
    Main gameplay state that handles all game logic during active play.
    
    This class manages:
    - Entity spawning and updates
    - Collision detection between player and game objects
    - Score and lives tracking
    - Game over conditions
    - Rendering of game objects and UI
    
    Attributes:
        pose_detector: Pose detection system for body tracking
        spawn_manager: Manages spawning of targets, obstacles, and powerups
        score_manager: Tracks player score and lives
        collision_detector: Handles collision detection logic
        game_renderer: Renders all game visuals
        start_time: Timestamp when gameplay started
        paused: Whether game is currently paused
    """
    
    def __init__(self, screen: pygame.Surface, sound_manager, pose_detector, game_renderer) -> None:
        """Initialize gameplay with screen, sound, pose detector, and renderer."""
        super().__init__(screen, sound_manager)
        self.pose_detector = pose_detector
        self.game_renderer = game_renderer
        
        # Initialize managers
        self.spawn_manager = SpawnManager(screen.get_width(), screen.get_height())
        self.score_manager = ScoreManager(starting_lives=config.STARTING_LIVES)
        self.collision_detector = CollisionDetector()
        
        # Game state tracking
        self.start_time: float = 0.0
        self.paused: bool = False
    
    def on_enter(self) -> None:
        """Start gameplay music and reset game to initial state."""
        try:
            self.sound_manager.play_music('gameplay', loops=-1, fade_ms=500)
        except Exception as e:
            print(f"[Warning] Failed to start gameplay music: {e}")
        
        self.reset_game()
        self.start_time = time.time()
    
    def on_exit(self) -> None:
        """Cleanup when leaving gameplay state."""
        self.paused = False
    
    def reset_game(self) -> None:
        """Reset score, lives, and clear all spawned entities."""
        self.score_manager.reset()
        self.spawn_manager.reset()
        self.paused = False
    
    def update(self, dt: float, landmarks: Optional[Any], hand_info: Dict[str, Any]) -> Optional[int]:
        """Update entities, check collisions, return GAME_OVER if no lives left."""
        if self.paused:
            return None
        
        # Update spawn manager (spawns new entities based on time and score)
        self.spawn_manager.update(dt, self.score_manager.score)
        
        # Update powerup timers
        self.score_manager.update_powerups(dt)
        
        # Handle collision detection
        if landmarks:
            self._handle_collisions(landmarks, hand_info)
        
        # Check for game over condition
        if self.score_manager.game_over:
            try:
                self.sound_manager.stop_music(fade_ms=500)
            except Exception as e:
                print(f"[Warning] Failed to stop music on game over: {e}")
            return config.GAME_OVER
        
        return None
    
    def _handle_collisions(self, landmarks: Any, hand_info: Dict[str, Any]) -> None:
        """Check collisions: fist hits targets, head hits obstacles, hand grabs powerups."""
        try:
            # Get head position for obstacle collision
            head_pos = self.pose_detector.get_landmark_position(
                landmarks, 
                0,  # Nose landmark index
                self.screen.get_width(), 
                self.screen.get_height()
            )
            
            # Check target hits with closed fists
            self._check_target_hits(hand_info)
            
            # Check obstacle collisions with head
            if head_pos:
                self._check_obstacle_collisions(head_pos)
            
            # Check powerup collection with open hands
            self._check_powerup_collection(hand_info)
            
        except Exception as e:
            print(f"[Error] Collision detection failed: {e}")
    
    def _check_target_hits(self, hand_info: Dict[str, Any]) -> None:
        """Check if closed fist hit any targets."""
        for hand_side in ['left_hand', 'right_hand']:
            hand_data = hand_info.get(hand_side, {})
            
            if hand_data.get('is_fist', False):
                hand_pos = hand_data.get('position')
                
                if hand_pos:
                    # Check collision with all targets
                    hit_target = self.collision_detector.check_hand_collision(
                        hand_pos, 
                        self.spawn_manager.targets
                    )
                    
                    if hit_target:
                        self._handle_target_hit(hit_target)
    
    def _check_obstacle_collisions(self, head_pos: tuple) -> None:
        """Check if obstacles hit player's head."""
        hit_obstacle = self.collision_detector.check_head_collision(
            head_pos, 
            self.spawn_manager.obstacles
        )
        
        if hit_obstacle:
            self._handle_obstacle_hit(hit_obstacle)
    
    def _check_powerup_collection(self, hand_info: Dict[str, Any]) -> None:
        """Check if open hand grabbed any powerups."""
        for hand_side in ['left_hand', 'right_hand']:
            hand_data = hand_info.get(hand_side, {})
            
            # Only grab with open hand (not fist)
            if not hand_data.get('is_fist', True):
                hand_pos = hand_data.get('position')
                
                if hand_pos:
                    grabbed_powerup = self.collision_detector.check_hand_collision(
                        hand_pos, 
                        self.spawn_manager.powerups
                    )
                    
                    if grabbed_powerup:
                        self._handle_powerup_grab(grabbed_powerup)
    
    def _handle_target_hit(self, target: Any) -> None:
        """Award points, remove target, play hit sound."""
        points = self.score_manager.hit_target()
        self.spawn_manager.remove_target(target)
        
        try:
            self.sound_manager.play_sound('hit')
        except Exception as e:
            print(f"[Warning] Failed to play hit sound: {e}")
    
    def _handle_obstacle_hit(self, obstacle: Any) -> None:
        """Reduce lives (unless shield active), remove obstacle, play sound."""
        self.score_manager.take_damage()
        self.spawn_manager.remove_obstacle(obstacle)
        
        try:
            self.sound_manager.play_sound('damage')
        except Exception as e:
            print(f"[Warning] Failed to play damage sound: {e}")
        
        # Check if game is over after taking damage
        if self.score_manager.game_over:
            try:
                self.sound_manager.play_sound('game_over')
            except Exception as e:
                print(f"[Warning] Failed to play game over sound: {e}")
    
    def _handle_powerup_grab(self, powerup: Any) -> None:
        """Activate powerup effect, remove powerup, play sound."""
        self.score_manager.collect_powerup(powerup.type)
        self.spawn_manager.remove_powerup(powerup)
        
        try:
            self.sound_manager.play_sound('powerup')
        except Exception as e:
            print(f"[Warning] Failed to play powerup sound: {e}")
    
    def render(self) -> None:
        """Draw background and game objects (targets, obstacles, powerups)."""
        # Draw background
        self.game_renderer.clear_screen()
        
        # Draw all game objects
        self.game_renderer.draw_game_objects(
            self.spawn_manager.targets,
            self.spawn_manager.obstacles,
            self.spawn_manager.powerups
        )
    
    def render_with_landmarks(self, landmarks: Optional[Any], hand_info: Dict[str, Any], clock: pygame.time.Clock) -> None:
        """Draw stickman, hand indicators, and UI (score, lives, FPS)."""
        try:
            # Draw stickman from pose
            if landmarks:
                self.game_renderer.draw_stickman(landmarks, self.pose_detector)
            
            # Draw hand indicators
            self.game_renderer.draw_hand_indicators(hand_info)
            
            # Draw UI (score, lives, powerups, FPS)
            self.game_renderer.draw_ui(self.score_manager, clock, hand_info)
            
        except Exception as e:
            print(f"[Error] Rendering failed: {e}")
    
    def handle_event(self, event: pygame.event.Event) -> Optional[int]:
        """Handle keyboard: ESC=menu, SPACE=pause."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return config.GAME_MENU
            elif event.key == pygame.K_SPACE:
                self.paused = not self.paused
        
        return None
    
    def get_play_duration(self) -> float:
        """Return elapsed time since gameplay started."""
        return time.time() - self.start_time
