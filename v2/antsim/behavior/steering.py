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


def strongest_trail_direction(
    grid: PheromoneGrid,
    layer: int,
    position: Vec2,
    distance: float,
    samples: int = 12,
) -> tuple[Vec2 | None, float]:
    """Szuka najsilniejszego śladu wokół mrówki (próbkowanie dookolne).

    Używane przy wejściu w nowy stan, by mrówka od razu zorientowała się wzdłuż
    istniejącego, wspólnego szlaku zamiast ruszać w przypadkowym kierunku.
    Zwraca (kierunek do najsilniejszego śladu, jego siła) lub (None, 0.0).
    """
    best_direction: Vec2 | None = None
    best_value = 0.0
    for i in range(samples):
        angle = (2.0 * math.pi / samples) * i
        direction = Vec2.from_angle(angle)
        point = position + direction * distance
        value = _sample_at(grid, layer, point)
        if value > best_value:
            best_value = value
            best_direction = direction
    return best_direction, best_value


def avoid_obstacles(position: Vec2, obstacles, lookahead: float) -> Vec2:
    """Wektor odpychający od pobliskich przeszkód (suma wkładów).

    Im bliżej powierzchni przeszkody, tym silniejszy wkład skierowany od niej.
    Złożony z bezwładnością i innymi składowymi pozwala mrówce płynnie opływać
    przeszkodę zamiast się o nią zakleszczać.
    """
    push = Vec2(0.0, 0.0)
    for obstacle in obstacles:
        nearest = obstacle.closest_point(position)
        offset = position - nearest
        distance = offset.length()
        if distance >= lookahead:
            continue
        if distance > 0.0:
            direction = offset.normalized()
        else:
            # Punkt wewnątrz przeszkody — pchaj od jej środka.
            direction = (position - obstacle.center).normalized()
        weight = (lookahead - distance) / lookahead
        push = push + direction * weight
    return push


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
