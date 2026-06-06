"""Wykresy szeregów czasowych (warstwa widoku).

Lekki wykres liniowy rysowany na powierzchni pygame oraz ``ChartPanel``, który
układa kilka wykresów w stos i zasila je danymi z ``StatsCollector.history``.
Czyta tylko gotowe próbki — nie liczy statystyk samodzielnie.
"""

from __future__ import annotations

from typing import Callable, Sequence

import pygame

_BG = (24, 24, 30)
_BORDER = (66, 66, 80)
_TEXT = (210, 210, 218)
_GRID = (44, 44, 54)


def draw_line_chart(surface: pygame.Surface, font: pygame.font.Font, rect: pygame.Rect,
                    title: str, values: Sequence[float], color: tuple[int, int, int],
                    fmt: str = "{:.0f}") -> None:
    """Rysuje pojedynczy wykres liniowy serii ``values`` w prostokącie ``rect``."""
    pygame.draw.rect(surface, _BG, rect, border_radius=4)
    pygame.draw.rect(surface, _BORDER, rect, 1, border_radius=4)

    latest = values[-1] if values else 0.0
    surface.blit(font.render(title, True, _TEXT), (rect.x + 6, rect.y + 3))
    value_text = font.render(fmt.format(latest), True, color)
    surface.blit(value_text, (rect.right - value_text.get_width() - 6, rect.y + 3))

    plot = pygame.Rect(rect.x + 6, rect.y + 20, rect.width - 12, rect.height - 26)
    pygame.draw.line(surface, _GRID, (plot.x, plot.bottom), (plot.right, plot.bottom), 1)

    if len(values) < 2:
        return

    lowest = min(values)
    highest = max(values)
    span = highest - lowest
    if span <= 0:
        span = 1.0
        lowest = highest - 0.5

    step_x = plot.width / (len(values) - 1)
    points = []
    for i, value in enumerate(values):
        x = plot.x + i * step_x
        normalized = (value - lowest) / span
        y = plot.bottom - normalized * plot.height
        points.append((x, y))
    pygame.draw.lines(surface, color, False, points, 2)


class ChartPanel:
    WIDTH = 250
    HEIGHT = 60
    GAP = 6
    PAD = 10

    def __init__(self, stats, config) -> None:
        self.stats = stats
        self.config = config
        self.font = pygame.font.Font(None, 22)
        # (tytuł, ekstraktor serii z historii, kolor, format wartości)
        self._charts: list[tuple[str, Callable[[list], list[float]], tuple, str]] = [
            ("Dostarczone /min", lambda h: [s.rate_per_min for s in h], (120, 220, 120), "{:.0f}"),
            ("Populacja", lambda h: [float(s.population) for s in h], (120, 170, 240), "{:.0f}"),
            ("Lacznie jedzenia", lambda h: [float(s.cumulative_food) for s in h], (240, 210, 110), "{:.0f}"),
            ("Wydajnosc /mrowke", lambda h: [s.efficiency for s in h], (240, 150, 90), "{:.2f}"),
        ]

    def draw(self, surface: pygame.Surface) -> None:
        if not self.config.show_charts:
            return
        history = list(self.stats.history)
        count = len(self._charts)
        total = count * self.HEIGHT + (count - 1) * self.GAP
        x = self.PAD
        y = self.config.height - 30 - total
        for title, extractor, color, fmt in self._charts:
            rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
            draw_line_chart(surface, self.font, rect, title, extractor(history), color, fmt)
            y += self.HEIGHT + self.GAP
