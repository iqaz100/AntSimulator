"""Kolektor statystyk (Observer) z szeregiem czasowym.

Subskrybuje zdarzenia świata (liczy dostarczenia) i co ustalony interwał zapisuje
próbkę stanu kolonii do ograniczonej historii. Historia zasila wykresy (Etap 6).
Moduł jest wolny od pygame — to czysta logika, łatwa do testów.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from antsim.core.events import EventBus


@dataclass(frozen=True)
class Sample:
    time: float           # czas symulacji [s]
    cumulative_food: int  # łącznie dostarczone jedzenie
    rate_per_min: float   # tempo dostarczeń w ostatnim interwale [szt./min]
    population: int        # liczebność kolonii
    efficiency: float      # dostarczenia na mrówkę na minutę


class StatsCollector:
    def __init__(self, events: EventBus, sample_interval: float = 1.0,
                 history_size: int = 240) -> None:
        self.food_delivered = 0
        self.elapsed_time = 0.0
        self.sample_interval = sample_interval
        self.history: deque[Sample] = deque(maxlen=history_size)

        self._since_sample = 0.0
        self._food_at_last_sample = 0
        events.subscribe("food_delivered", self._on_food_delivered)

    def _on_food_delivered(self, **_payload) -> None:
        self.food_delivered += 1

    def tick(self, dt: float, world) -> None:
        self.elapsed_time += dt
        self._since_sample += dt
        if self._since_sample < self.sample_interval:
            return

        delivered = self.food_delivered - self._food_at_last_sample
        rate = delivered / (self._since_sample / 60.0)
        population = len(world.ants)
        efficiency = rate / population if population else 0.0
        self.history.append(
            Sample(self.elapsed_time, self.food_delivered, rate, population, efficiency)
        )
        self._food_at_last_sample = self.food_delivered
        self._since_sample = 0.0
