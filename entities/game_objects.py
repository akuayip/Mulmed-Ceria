"""Target, Obstacle, and PowerUp classes for the game."""

import pygame
import random
import math  
from typing import Tuple


class GameObject:
    """Base class for all game objects."""

    def __init__(self, x: int, y: int, radius: int, color: Tuple[int, int, int], speed: float) -> None:
        """Initialize game object."""
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = speed
        self.active = True

    def update(self, dt: float) -> None:
        """Update object position."""
        pass  # To be overridden by subclasses

    def draw(self, surface: pygame.Surface) -> None:
        """Draw object on surface."""
        if self.active:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def get_position(self) -> Tuple[int, int]:
        """Get object center position."""
        return (int(self.x), int(self.y))


class Target(GameObject):
    """Target object that player should punch for points."""
    DEFAULT_RADIUS = 25
    SPEED_RANGE = (50, 150)  # (min_speed, max_speed)
    POINTS = 10
    COLOR = (0, 255, 0)  # Green

    def __init__(self, x: int, y: int, screen_width: int, screen_height: int) -> None:
        """Initialize target."""
        super().__init__(
            x, y,
            radius=self.DEFAULT_RADIUS,
            color=self.COLOR,
            speed=random.uniform(*self.SPEED_RANGE)  
        )
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.direction_x = random.choice([-1, 1])
        self.direction_y = random.choice([-1, 1])
        self.points = self.POINTS

    def update(self, dt: float) -> None:
        """Move target and bounce off walls."""
        if not self.active:
            return

        self.x += self.direction_x * self.speed * dt
        self.y += self.direction_y * self.speed * dt

        if self.x - self.radius <= 0 or self.x + self.radius >= self.screen_width:
            self.direction_x *= -1
            self.x = max(self.radius, min(self.x, self.screen_width - self.radius))

        if self.y - self.radius <= 0 or self.y + self.radius >= self.screen_height:
            self.direction_y *= -1
            self.y = max(self.radius, min(self.y, self.screen_height - self.radius))

    def draw(self, surface: pygame.Surface) -> None:
        """Draw target with inner circle."""
        if self.active:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), self.radius // 2)
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 5)


class Obstacle(GameObject):
    """Obstacle object that damages player if hit."""
    DEFAULT_RADIUS = 30
    SPEED_RANGE = (80, 200)
    COLOR = (255, 0, 0)  # Red
    DAMAGE = 20
    LIVES_COST = 1
    LIFETIME = 10.0  # Seconds
    DEACTIVATE_DISTANCE = 50  # Distance from target to deactivate

    def __init__(self, x: int, y: int, screen_width: int, screen_height: int) -> None:
        """Initialize obstacle."""
        super().__init__(
            x, y,
            radius=self.DEFAULT_RADIUS,
            color=self.COLOR,
            speed=random.uniform(*self.SPEED_RANGE)
        )
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.damage = self.DAMAGE
        self.lives_cost = self.LIVES_COST
        self.time_alive = 0
        
        self.target_x = self.screen_width // 2 + random.randint(-100, 100)
        self.target_y = self.screen_height // 2 + random.randint(-100, 100)

    def update(self, dt: float) -> None:
        """Move obstacle towards player (center-ish)."""
        if not self.active:
            return

        # Update lifetime
        self.time_alive += dt
        if self.time_alive >= self.LIFETIME:
            self.active = False
            return

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = (dx**2 + dy**2) ** 0.5

        if distance < self.DEACTIVATE_DISTANCE:
            self.active = False
            return

        if distance > 0:
            self.x += (dx / distance) * self.speed * dt
            self.y += (dy / distance) * self.speed * dt

    def draw(self, surface: pygame.Surface) -> None:
        """Draw obstacle with warning sign."""
        if self.active:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.line(
                surface, (255, 255, 255),
                (int(self.x - 10), int(self.y - 10)),
                (int(self.x + 10), int(self.y + 10)), 3
            )
            pygame.draw.line(
                surface, (255, 255, 255),
                (int(self.x + 10), int(self.y - 10)),
                (int(self.x - 10), int(self.y + 10)), 3
            )


class PowerUp(GameObject):
    """Power-up object that gives player bonus."""
    TYPES = ['shield', 'double_score', 'slow_motion']
    DEFAULT_RADIUS = 20
    COLOR = (255, 255, 0)  # Yellow
    SPEED = 100  
    LIFETIME = 5.0  # Seconds

    def __init__(self, x: int, y: int, screen_width: int, screen_height: int) -> None:
        """Initialize power-up."""
        super().__init__(
            x, y,
            radius=self.DEFAULT_RADIUS,
            color=self.COLOR,
            speed=self.SPEED
        )
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.type = random.choice(self.TYPES)
        self.time_alive = 0

    def update(self, dt: float) -> None:
        """Update power-up (floating effect)."""
        if not self.active:
            return

        self.time_alive += dt
        if self.time_alive >= self.LIFETIME:
            self.active = False
            return

        # Floating effect (sine wave)
        self.y += math.sin(self.time_alive * 3) * 2

    def draw(self, surface: pygame.Surface) -> None:
        """Draw power-up with star effect."""
        if self.active:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            
            # Star points
            points = []
            for i in range(5):
                angle = math.pi * 2 * i / 5 - math.pi / 2
                px = self.x + math.cos(angle) * (self.radius - 5)
                py = self.y + math.sin(angle) * (self.radius - 5)
                points.append((int(px), int(py)))
            if len(points) >= 3:
                pygame.draw.polygon(surface, (255, 165, 0), points)