"""
Game Objects Module
Defines Target, Obstacle, and PowerUp classes for the game.
"""

import pygame
import random
from typing import Tuple


class GameObject:
    """Base class for all game objects."""

    def __init__(self, x: int, y: int, radius: int, color: Tuple[int, int, int], speed: float):
        """
        Initialize game object.

        Args:
            x: X position
            y: Y position
            radius: Object radius
            color: RGB color tuple
            speed: Movement speed
        """
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = speed
        self.active = True

    def update(self, dt: float):
        """Update object position."""
        pass

    def draw(self, surface: pygame.Surface):
        """Draw object on surface."""
        if self.active:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def get_position(self) -> Tuple[int, int]:
        """Get object center position."""
        return (int(self.x), int(self.y))


class Target(GameObject):
    """
    Target object that player should punch for points.
    """

    def __init__(self, x: int, y: int, screen_width: int, screen_height: int):
        """
        Initialize Target.

        Args:
            x: Starting X position
            y: Starting Y position
            screen_width: Width of game screen
            screen_height: Height of game screen
        """
        # Green circle for target
        super().__init__(x, y, radius=25, color=(0, 255, 0), speed=random.uniform(50, 150))
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.direction_x = random.choice([-1, 1])
        self.direction_y = random.choice([-1, 1])
        self.points = 10

    def update(self, dt: float):
        """Move target and bounce off walls."""
        if not self.active:
            return

        # Update position
        self.x += self.direction_x * self.speed * dt
        self.y += self.direction_y * self.speed * dt

        # Bounce off walls
        if self.x - self.radius <= 0 or self.x + self.radius >= self.screen_width:
            self.direction_x *= -1
            self.x = max(self.radius, min(self.x, self.screen_width - self.radius))

        if self.y - self.radius <= 0 or self.y + self.radius >= self.screen_height:
            self.direction_y *= -1
            self.y = max(self.radius, min(self.y, self.screen_height - self.radius))

    def draw(self, surface: pygame.Surface):
        """Draw target with inner circle."""
        if self.active:
            # Outer circle
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            # Inner circle (bullseye)
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), self.radius // 2)
            # Center dot
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 5)


class Obstacle(GameObject):
    """
    Obstacle object that damages player if hit.
    """

    def __init__(self, x: int, y: int, screen_width: int, screen_height: int):
        """
        Initialize Obstacle.

        Args:
            x: Starting X position
            y: Starting Y position
            screen_width: Width of game screen
            screen_height: Height of game screen
        """
        # Red circle for obstacle
        super().__init__(x, y, radius=30, color=(255, 0, 0), speed=random.uniform(80, 200))
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.damage = 20
        self.lives_cost = 1

    def update(self, dt: float):
        """Move obstacle towards player (center-ish)."""
        if not self.active:
            return

        # Move towards center with some randomness
        target_x = self.screen_width // 2 + random.randint(-100, 100)
        target_y = self.screen_height // 2 + random.randint(-100, 100)

        # Calculate direction
        dx = target_x - self.x
        dy = target_y - self.y
        distance = (dx**2 + dy**2) ** 0.5

        if distance > 0:
            self.x += (dx / distance) * self.speed * dt
            self.y += (dy / distance) * self.speed * dt

    def draw(self, surface: pygame.Surface):
        """Draw obstacle with warning sign."""
        if self.active:
            # Main circle
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            # Warning cross
            pygame.draw.line(
                surface,
                (255, 255, 255),
                (int(self.x - 10), int(self.y - 10)),
                (int(self.x + 10), int(self.y + 10)),
                3
            )
            pygame.draw.line(
                surface,
                (255, 255, 255),
                (int(self.x + 10), int(self.y - 10)),
                (int(self.x - 10), int(self.y + 10)),
                3
            )


class PowerUp(GameObject):
    """
    Power-up object that gives player bonus.
    """

    TYPES = ['shield', 'double_score', 'slow_motion']

    def __init__(self, x: int, y: int, screen_width: int, screen_height: int):
        """
        Initialize PowerUp.

        Args:
            x: Starting X position
            y: Starting Y position
            screen_width: Width of game screen
            screen_height: Height of game screen
        """
        # Yellow circle for power-up
        super().__init__(x, y, radius=20, color=(255, 255, 0), speed=100)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.type = random.choice(self.TYPES)
        self.lifetime = 5.0  # Disappear after 5 seconds
        self.time_alive = 0

    def update(self, dt: float):
        """Update power-up (floating effect)."""
        if not self.active:
            return

        self.time_alive += dt
        if self.time_alive >= self.lifetime:
            self.active = False
            return

        # Floating effect (sine wave)
        import math
        self.y += math.sin(self.time_alive * 3) * 2

    def draw(self, surface: pygame.Surface):
        """Draw power-up with star effect."""
        if self.active:
            # Main circle
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            # Star points
            points = []
            import math
            for i in range(5):
                angle = math.pi * 2 * i / 5 - math.pi / 2
                px = self.x + math.cos(angle) * (self.radius - 5)
                py = self.y + math.sin(angle) * (self.radius - 5)
                points.append((int(px), int(py)))
            if len(points) >= 3:
                pygame.draw.polygon(surface, (255, 165, 0), points)
