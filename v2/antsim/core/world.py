"""Świat symulacji — agregat (Aggregate Root).

Jedyny właściciel stanu: gniazdo, mrówki, jedzenie, przeszkody i siatka
feromonów. Udostępnia też zapytania przestrzenne używane przez zachowania.
Nie wie nic o pygame ani o renderowaniu.
"""

from __future__ import annotations

from antsim.core.events import EventBus
from antsim.core.vector import Vec2
from antsim.entities.food import Food
from antsim.entities.nest import Nest
from antsim.entities.obstacle import Obstacle
from antsim.pheromones.grid import PheromoneGrid
from config.settings import SimulationConfig


class World:
    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.events = EventBus()
        self.nest = Nest(Vec2(config.width / 2.0, config.height / 2.0), config.nest_radius)
        self.ants: list = []
        self.foods: list[Food] = []
        self.obstacles: list[Obstacle] = []
        self.pheromones = PheromoneGrid(
            width=config.width,
            height=config.height,
            cell_size=config.cell_size,
            evaporation=config.evaporation,
            diffusion=config.diffusion,
            max_value=config.deposit_max,
        )

    def point_in_obstacle(self, point: Vec2) -> bool:
        """Czy punkt leży wewnątrz którejkolwiek przeszkody."""
        return any(obstacle.contains(point) for obstacle in self.obstacles)

    def nearest_food(self, position: Vec2, radius: float) -> Food | None:
        """Najbliższe niepuste źródło jedzenia w zasięgu ``radius`` (lub None)."""
        best: Food | None = None
        best_distance_sq = radius * radius
        for food in self.foods:
            if food.is_empty():
                continue
            distance_sq = position.distance_sq_to(food.position)
            if distance_sq <= best_distance_sq:
                best_distance_sq = distance_sq
                best = food
        return best
