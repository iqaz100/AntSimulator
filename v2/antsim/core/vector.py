"""Lekki, niezmienny wektor 2D (value object).

Używany w całej warstwie modelu zamiast luźnych par (x, y). Niezmienność
(frozen dataclass) chroni przed przypadkowymi efektami ubocznymi przy
współdzieleniu pozycji między obiektami.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Vec2:
    x: float = 0.0
    y: float = 0.0

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vec2":
        return Vec2(self.x * scalar, self.y * scalar)

    __rmul__ = __mul__

    def __truediv__(self, scalar: float) -> "Vec2":
        return Vec2(self.x / scalar, self.y / scalar)

    def length(self) -> float:
        return math.hypot(self.x, self.y)

    def length_sq(self) -> float:
        return self.x * self.x + self.y * self.y

    def normalized(self) -> "Vec2":
        length = self.length()
        if length == 0.0:
            return Vec2(0.0, 0.0)
        return Vec2(self.x / length, self.y / length)

    def angle(self) -> float:
        return math.atan2(self.y, self.x)

    def rotated(self, radians: float) -> "Vec2":
        cos_a = math.cos(radians)
        sin_a = math.sin(radians)
        return Vec2(self.x * cos_a - self.y * sin_a, self.x * sin_a + self.y * cos_a)

    def distance_to(self, other: "Vec2") -> float:
        return (self - other).length()

    def distance_sq_to(self, other: "Vec2") -> float:
        return (self - other).length_sq()

    @staticmethod
    def from_angle(radians: float, length: float = 1.0) -> "Vec2":
        return Vec2(math.cos(radians) * length, math.sin(radians) * length)


def wrap_to_pi(angle: float) -> float:
    """Sprowadza kąt do przedziału (-pi, pi]."""
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle <= -math.pi:
        angle += 2.0 * math.pi
    return angle
