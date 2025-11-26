"""
Spawn Manager Module

This module contains the SpawnManager class which handles all logic for
spawning game objects (targets, obstacles, power-ups) with adaptive timing.
"""
import random
from typing import List
from entities.game_objects import Target, Obstacle, PowerUp


class SpawnManager:
    """
    Manages the timing and logic for spawning all game objects.
    
    This class handles:
    - Timed spawning of targets, obstacles, and power-ups
    - Adaptive spawn rates based on current score/level
    - Random positioning within screen bounds
    - Entity list management (adding/removing objects)
    
    Attributes:
        screen_width: Width of the game screen
        screen_height: Height of the game screen
        targets: List of active target objects
        obstacles: List of active obstacle objects
        powerups: List of active power-up objects
        target_spawn_timer: Time until next target spawn
        target_spawn_interval: Seconds between target spawns
        obstacle_spawn_timer: Time until next obstacle spawn
        obstacle_spawn_interval: Seconds between obstacle spawns
        powerup_spawn_timer: Time until next power-up spawn
        powerup_spawn_interval: Seconds between power-up spawns
    """

    def __init__(self, screen_width: int, screen_height: int) -> None:
        """Initialize spawn manager with screen dimensions."""
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height

        # Entity lists
        self.targets: List[Target] = []
        self.obstacles: List[Obstacle] = []
        self.powerups: List[PowerUp] = []

        # Spawn timers
        self.target_spawn_timer: float = 0.0
        self.target_spawn_interval: float = 3.0  # Spawn target every 3 seconds
        self.obstacle_spawn_timer: float = 0.0
        self.obstacle_spawn_interval: float = 5.0  # Spawn obstacle every 5 seconds
        self.powerup_spawn_timer: float = 0.0
        self.powerup_spawn_interval: float = 15.0  # Spawn powerup every 15 seconds

    def update_screen_size(self, w: int, h: int) -> None:
        """Update screen dimensions when window resized."""
        self.screen_width = w
        self.screen_height = h

    def update(self, dt: float, current_score: int = 0) -> None:
        """Update spawn timers, create entities when ready, increase difficulty with score."""
        # Adjust spawn rates based on score (increase difficulty)
        score_factor = 1 + (current_score // 1000) * 0.1  # Increase by 10% every 1000 points
        adjusted_target_interval = max(1.5, self.target_spawn_interval / score_factor)
        adjusted_obstacle_interval = max(3.0, self.obstacle_spawn_interval / score_factor)

        # Update spawn timers
        self.target_spawn_timer += dt
        self.obstacle_spawn_timer += dt
        self.powerup_spawn_timer += dt

        # Spawn objects when timers exceed intervals
        if self.target_spawn_timer >= adjusted_target_interval:
            self.spawn_target()
            self.target_spawn_timer = 0.0

        if self.obstacle_spawn_timer >= adjusted_obstacle_interval:
            self.spawn_obstacle()
            self.obstacle_spawn_timer = 0.0

        if self.powerup_spawn_timer >= self.powerup_spawn_interval:
            self.spawn_powerup()
            self.powerup_spawn_timer = 0.0

        # Update all entities
        self._update_entities(dt)

    def _update_entities(self, dt: float) -> None:
        """Update all entities and remove expired/off-screen ones."""
        # Update targets and remove destroyed ones
        for target in self.targets[:]:
            target.update(dt)
            if target.lifetime <= 0:
                self.targets.remove(target)

        # Update obstacles and remove off-screen ones
        for obstacle in self.obstacles[:]:
            obstacle.update(dt)
            if not obstacle.is_on_screen():
                self.obstacles.remove(obstacle)

        # Update powerups and remove expired ones
        for powerup in self.powerups[:]:
            powerup.update(dt)
            if powerup.lifetime <= 0:
                self.powerups.remove(powerup)
            
    def reset(self) -> None:
        """Clear all entities and reset timers."""
        self.targets.clear()
        self.obstacles.clear()
        self.powerups.clear()
        
        self.target_spawn_timer = 0.0
        self.obstacle_spawn_timer = 0.0
        self.powerup_spawn_timer = 0.0

    def spawn_target(self) -> None:
        """Spawn target at random position within bounds."""
        x = random.randint(100, self.screen_width - 100)
        y = random.randint(100, self.screen_height - 100)
        self.targets.append(Target(x, y, self.screen_width, self.screen_height))

    def spawn_obstacle(self) -> None:
        """Spawn obstacle from random screen edge."""
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        
        if edge == 'top':
            x = random.randint(0, self.screen_width)
            y = -50
        elif edge == 'bottom':
            x = random.randint(0, self.screen_width)
            y = self.screen_height + 50
        elif edge == 'left':
            x = -50
            y = random.randint(0, self.screen_height)
        else:  # right
            x = self.screen_width + 50
            y = random.randint(0, self.screen_height)
        
        self.obstacles.append(Obstacle(x, y, self.screen_width, self.screen_height))

    def spawn_powerup(self) -> None:
        """Spawn powerup at random position within bounds."""
        x = random.randint(100, self.screen_width - 100)
        y = random.randint(100, self.screen_height - 100)
        self.powerups.append(PowerUp(x, y, self.screen_width, self.screen_height))

    def remove_target(self, target: Target) -> None:
        """Remove specific target from list."""
        if target in self.targets:
            self.targets.remove(target)

    def remove_obstacle(self, obstacle: Obstacle) -> None:
        """Remove specific obstacle from list."""
        if obstacle in self.obstacles:
            self.obstacles.remove(obstacle)

    def remove_powerup(self, powerup: PowerUp) -> None:
        """Remove specific powerup from list."""
        if powerup in self.powerups:
            self.powerups.remove(powerup)