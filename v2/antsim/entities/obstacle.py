"""Prostokątna przeszkoda (pełne wykorzystanie w Etapie 4)."""

from __future__ import annotations

from antsim.core.vector import Vec2


class Obstacle:
    def __init__(self, x: float, y: float, width: float, height: float) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def center(self) -> Vec2:
        return Vec2(self.x + self.width / 2.0, self.y + self.height / 2.0)

    def contains(self, point: Vec2) -> bool:
        return (
            self.x <= point.x <= self.x + self.width
            and self.y <= point.y <= self.y + self.height
        )

    def closest_point(self, point: Vec2) -> Vec2:
        """Najbliższy punkt prostokąta względem ``point`` (sam punkt, gdy w środku)."""
        closest_x = max(self.x, min(point.x, self.x + self.width))
        closest_y = max(self.y, min(point.y, self.y + self.height))
        return Vec2(closest_x, closest_y)

    def distance_to(self, point: Vec2) -> float:
        """Odległość punktu od najbliższej krawędzi prostokąta (0 w środku)."""
        return self.closest_point(point).distance_to(point)
