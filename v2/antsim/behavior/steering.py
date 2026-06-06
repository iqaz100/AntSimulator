"""Składowe sterowania ruchem mrówki (Strategy).

Każda funkcja zwraca *wektor wkładu* w pożądany kierunek. Stan mrówki składa je
w JEDEN wektor na klatkę (z wagami z konfiguracji) i dopiero ten wynik wyznacza
docelowy kierunek. Dzięki temu nie ma "walki o kąt" wielu systemów naraz, która
w v1 powodowała kręcenie się w kółko.
"""

from __future__ import annotations

import math
import random

from config.settings import SimulationConfig
from antsim.core.vector import Vec2
from antsim.pheromones.grid import PheromoneGrid


def wander(heading: Vec2) -> Vec2:
    """Losowy, jednostkowy szum dorzucany do kierunku (delikatne błądzenie)."""
    return Vec2.from_angle(random.uniform(0.0, 2.0 * math.pi))


def seek(position: Vec2, target: Vec2) -> Vec2:
    """Jednostkowy wektor w stronę celu."""
    return (target - position).normalized()


def follow_pheromone(
    grid: PheromoneGrid,
    layer: int,
    position: Vec2,
    heading: Vec2,
    cfg: SimulationConfig,
) -> tuple[Vec2, float]:
    """Próbkuje siatkę trzema czujnikami (lewo/środek/prawo) wzdłuż kierunku.

    Zwraca (kierunek, siła). Mrówka skręca ku najsilniejszemu sygnałowi; gdy
    środek jest najmocniejszy — idzie prosto. To klasyczny, stabilny mechanizm.
    """
    left_dir = heading.rotated(cfg.sensor_angle)
    right_dir = heading.rotated(-cfg.sensor_angle)

    center = _sample_at(grid, layer, position + heading * cfg.sensor_distance)
    left = _sample_at(grid, layer, position + left_dir * cfg.sensor_distance)
    right = _sample_at(grid, layer, position + right_dir * cfg.sensor_distance)

    if center >= left and center >= right:
        return heading, center
    if left >= right:
        return left_dir, left
    return right_dir, right


def avoid_edges(position: Vec2, width: float, height: float, margin: float) -> Vec2:
    """Wektor odpychający od krawędzi planszy (zero z dala od brzegów)."""
    push = Vec2(0.0, 0.0)
    if position.x < margin:
        push = push + Vec2(1.0, 0.0)
    elif position.x > width - margin:
        push = push + Vec2(-1.0, 0.0)
    if position.y < margin:
        push = push + Vec2(0.0, 1.0)
    elif position.y > height - margin:
        push = push + Vec2(0.0, -1.0)
    return push


def _sample_at(grid: PheromoneGrid, layer: int, point: Vec2) -> float:
    return grid.sample(layer, point.x, point.y)
