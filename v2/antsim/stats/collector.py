"""Kolektor statystyk (Observer).

Subskrybuje zdarzenia świata i utrzymuje liczniki. Rozbudowa o wykresy w czasie
nastąpi w Etapie 6.
"""

from __future__ import annotations

from antsim.core.events import EventBus


class StatsCollector:
    def __init__(self, events: EventBus) -> None:
        self.food_delivered = 0
        self.elapsed_time = 0.0
        events.subscribe("food_delivered", self._on_food_delivered)

    def _on_food_delivered(self, **_payload) -> None:
        self.food_delivered += 1

    def tick(self, dt: float) -> None:
        self.elapsed_time += dt
