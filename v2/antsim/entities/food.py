"""Źródło jedzenia o ograniczonym zapasie."""

from __future__ import annotations

from antsim.core.vector import Vec2


class Food:
    def __init__(self, position: Vec2, amount: int, radius: float) -> None:
        self.position = position
        self.amount = amount
        self.max_amount = amount
        self.radius = radius

    def take(self, amount: int = 1) -> int:
        """Pobiera porcję; zwraca ile faktycznie udało się pobrać."""
        taken = min(amount, self.amount)
        self.amount -= taken
        return taken

    def is_empty(self) -> bool:
        return self.amount <= 0

    def fill_ratio(self) -> float:
        if self.max_amount == 0:
            return 0.0
        return self.amount / self.max_amount

    def contains(self, point: Vec2) -> bool:
        return self.position.distance_to(point) <= self.radius
