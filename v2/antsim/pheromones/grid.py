"""Siatka feromonów oparta na numpy.

Świat jest dzielony na komórki o boku ``cell_size``. Trzymamy dwie warstwy:

* ``HOME`` — ślad "do domu", zostawiany przez mrówki szukające jedzenia,
* ``FOOD`` — ślad "do jedzenia", zostawiany przez mrówki wracające z łupem.

Co krok symulacji warstwy **parują** (mnożenie przez współczynnik < 1) oraz
opcjonalnie **dyfundują** (rozmycie do sąsiednich komórek). To zastępuje listę
osobnych obiektów-kropli z v1 (która dawała przeszukiwanie O(n^2)).
"""

from __future__ import annotations

import numpy as np


class PheromoneGrid:
    HOME = 0
    FOOD = 1

    def __init__(
        self,
        width: int,
        height: int,
        cell_size: int,
        evaporation: float,
        diffusion: float,
        max_value: float,
    ) -> None:
        self.cell_size = cell_size
        self.cols = max(1, width // cell_size)
        self.rows = max(1, height // cell_size)
        self.evaporation = evaporation
        self.diffusion = diffusion
        self.max_value = max_value
        # Kształt: (warstwa, wiersz, kolumna)
        self.grid = np.zeros((2, self.rows, self.cols), dtype=np.float32)

    def _to_cell(self, x: float, y: float) -> tuple[int, int]:
        return int(y // self.cell_size), int(x // self.cell_size)

    def _in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def deposit(self, layer: int, x: float, y: float, amount: float) -> None:
        """Dodaje feromon w komórce zawierającej punkt (x, y)."""
        row, col = self._to_cell(x, y)
        if self._in_bounds(row, col):
            value = self.grid[layer, row, col] + amount
            self.grid[layer, row, col] = min(value, self.max_value)

    def sample(self, layer: int, x: float, y: float) -> float:
        """Zwraca natężenie feromonu w punkcie (x, y); poza siatką -> 0."""
        row, col = self._to_cell(x, y)
        if self._in_bounds(row, col):
            return float(self.grid[layer, row, col])
        return 0.0

    def update(self, dt: float) -> None:
        """Jeden krok: parowanie, a następnie dyfuzja."""
        self._evaporate(dt)
        if self.diffusion > 0.0:
            self._diffuse(dt)

    def _evaporate(self, dt: float) -> None:
        retain = max(0.0, 1.0 - self.evaporation * dt)
        self.grid *= retain

    def _diffuse(self, dt: float) -> None:
        amount = min(1.0, self.diffusion * dt)
        neighbors = (
            np.roll(self.grid, 1, axis=1)
            + np.roll(self.grid, -1, axis=1)
            + np.roll(self.grid, 1, axis=2)
            + np.roll(self.grid, -1, axis=2)
        ) * 0.25
        self.grid = self.grid * (1.0 - amount) + neighbors * amount

    def clear(self) -> None:
        self.grid.fill(0.0)
