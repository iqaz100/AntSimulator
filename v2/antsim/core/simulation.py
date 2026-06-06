"""Symulacja — orkiestracja kroku modelu.

Buduje świat z konfiguracji (fabryka) i wykonuje kolejne kroki czasu. Jest
całkowicie niezależna od pygame, więc daje się testować jednostkowo.
"""

from __future__ import annotations

import math
import random

from antsim.behavior.states import SearchingState
from antsim.core.vector import Vec2
from antsim.core.world import World
from antsim.entities.ant import Ant
from antsim.entities.food import Food
from antsim.entities.obstacle import Obstacle
from antsim.pheromones.grid import PheromoneGrid
from antsim.stats.collector import StatsCollector
from config.settings import SimulationConfig


class Simulation:
    def __init__(self, config: SimulationConfig, seed: int | None = None) -> None:
        if seed is not None:
            random.seed(seed)
        self.config = config
        self.world = World(config)
        self.stats = StatsCollector(
            self.world.events,
            sample_interval=config.stats_sample_interval,
            history_size=config.stats_history_size,
        )
        self._populate()

    # --- Budowa stanu początkowego (fabryka) ---

    def _populate(self) -> None:
        self._spawn_ants(self.config.ant_count)
        for _ in range(self.config.food_source_count):
            self._spawn_food()

    def _spawn_ants(self, count: int) -> None:
        nest = self.world.nest
        for _ in range(count):
            offset = Vec2.from_angle(
                random.uniform(0.0, 2.0 * math.pi),
                random.uniform(0.0, nest.radius),
            )
            self.world.ants.append(Ant(nest.position + offset, SearchingState()))

    def _spawn_food(self) -> None:
        cfg = self.config
        nest = self.world.nest
        for _ in range(50):
            position = Vec2(
                random.uniform(cfg.food_radius, cfg.width - cfg.food_radius),
                random.uniform(cfg.food_radius, cfg.height - cfg.food_radius),
            )
            if position.distance_to(nest.position) >= cfg.food_min_distance_from_nest:
                self.world.foods.append(Food(position, cfg.food_amount, cfg.food_radius))
                return

    # --- Interakcja użytkownika (sterowanie) ---

    def add_ants(self, count: int) -> None:
        self._spawn_ants(count)

    def set_population(self, target: int) -> None:
        """Ustawia liczebność kolonii — dodaje nowe lub usuwa nadmiarowe mrówki."""
        target = max(0, target)
        current = len(self.world.ants)
        if target > current:
            self._spawn_ants(target - current)
        elif target < current:
            del self.world.ants[target:]

    def add_food_at(self, position: Vec2) -> None:
        cfg = self.config
        self.world.foods.append(Food(position, cfg.food_amount, cfg.food_radius))

    def add_obstacle_at(self, position: Vec2) -> None:
        """Stawia kwadratową przeszkodę wyśrodkowaną na punkcie.

        Pomija miejsce na gnieździe oraz punkty już pokryte przeszkodą — dzięki
        temu trzymanie PPM maluje ścianę bez nakładania duplikatów co klatkę.
        """
        cfg = self.config
        size = cfg.obstacle_place_size
        if position.distance_to(self.world.nest.position) < self.world.nest.radius + size:
            return
        if self.world.point_in_obstacle(position):
            return
        self.world.obstacles.append(
            Obstacle(position.x - size / 2.0, position.y - size / 2.0, size, size)
        )

    def resize(self, width: int, height: int) -> None:
        """Dopasowuje świat do nowych wymiarów okna (np. pełny ekran).

        Buduje nową siatkę feromonów, przenosząc nakładający się fragment starej
        (szlaki nie znikają przy zmianie rozmiaru), oraz przycina pozycje mrówek
        i gniazda do nowych granic.
        """
        width = max(1, int(width))
        height = max(1, int(height))
        self.config.width = width
        self.config.height = height

        old = self.world.pheromones
        new_grid = PheromoneGrid(
            width, height, self.config.cell_size,
            old.evaporation, old.diffusion, old.max_value,
        )
        rows = min(old.rows, new_grid.rows)
        cols = min(old.cols, new_grid.cols)
        new_grid.grid[:, :rows, :cols] = old.grid[:, :rows, :cols]
        self.world.pheromones = new_grid

        clamp = lambda v, hi: max(0.0, min(hi, v))
        for ant in self.world.ants:
            ant.position = Vec2(clamp(ant.position.x, width), clamp(ant.position.y, height))
        nest = self.world.nest
        nest.position = Vec2(clamp(nest.position.x, width), clamp(nest.position.y, height))

    def clear_obstacles(self) -> None:
        self.world.obstacles.clear()

    def clear_pheromones(self) -> None:
        self.world.pheromones.clear()

    # --- Krok symulacji ---

    def step(self, dt: float) -> None:
        for ant in self.world.ants:
            ant.update(self.world, dt)
        self.world.pheromones.update(dt)
        self._prune_depleted_food()
        self.stats.tick(dt, self.world)

    def _prune_depleted_food(self) -> None:
        """Usuwa wyczerpane źródła jedzenia (np. po wielu kliknięciach myszą)."""
        if any(food.is_empty() for food in self.world.foods):
            self.world.foods = [food for food in self.world.foods if not food.is_empty()]
