"""Gniazdo kolonii — punkt startu i celu powrotu mrówek."""

from __future__ import annotations

from antsim.core.vector import Vec2


class Nest:
    def __init__(self, position: Vec2, radius: float) -> None:
        self.position = position
        self.radius = radius
        self.food_stored = 0

    def store_food(self, amount: int = 1) -> None:
        self.food_stored += amount

    def contains(self, point: Vec2) -> bool:
        return self.position.distance_to(point) <= self.radius
