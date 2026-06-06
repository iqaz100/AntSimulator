"""Warstwa widoku — rysuje świat na powierzchni pygame.

Renderer jest jedynym miejscem zależnym od pygame w warstwie prezentacji modelu.
Feromony rysowane są zbiorczo z tablicy numpy (warstwa HOME -> niebieski,
FOOD -> zielony), a obiekty na wierzchu.
"""

from __future__ import annotations

import numpy as np
import pygame

from antsim.core.world import World

_ANT_SEARCHING = (235, 90, 70)
_ANT_CARRYING = (245, 200, 70)
_NEST_COLOR = (150, 110, 70)
_FOOD_COLOR = (120, 220, 120)
_HEADING_COLOR = (20, 20, 25)
_TEXT_COLOR = (230, 230, 235)


class Renderer:
    def __init__(self, surface: pygame.Surface, config) -> None:
        self.surface = surface
        self.config = config
        self.font = pygame.font.Font(None, 26)

    def draw(self, world: World, fps: float) -> None:
        self.surface.fill(self.config.background_color)
        if self.config.show_pheromones:
            self._draw_pheromones(world)
        self._draw_food(world)
        self._draw_nest(world)
        self._draw_ants(world)
        self._draw_hud(world, fps)

    def _draw_pheromones(self, world: World) -> None:
        grid = world.pheromones
        home = grid.grid[grid.HOME]
        food = grid.grid[grid.FOOD]
        # surfarray oczekuje (szerokość, wysokość, 3) -> transpozycja (rows,cols)->(cols,rows)
        rgb = np.zeros((grid.cols, grid.rows, 3), dtype=np.uint8)
        rgb[..., 1] = np.clip(food.T, 0, 255).astype(np.uint8)   # zielony = do jedzenia
        rgb[..., 2] = np.clip(home.T, 0, 255).astype(np.uint8)   # niebieski = do domu
        layer = pygame.surfarray.make_surface(rgb)
        scaled = pygame.transform.scale(
            layer, (grid.cols * grid.cell_size, grid.rows * grid.cell_size)
        )
        self.surface.blit(scaled, (0, 0))

    def _draw_food(self, world: World) -> None:
        for food in world.foods:
            if food.is_empty():
                continue
            radius = int(food.radius * (0.4 + 0.6 * food.fill_ratio()))
            pygame.draw.circle(
                self.surface, _FOOD_COLOR, (int(food.position.x), int(food.position.y)), radius
            )

    def _draw_nest(self, world: World) -> None:
        nest = world.nest
        pygame.draw.circle(
            self.surface, _NEST_COLOR, (int(nest.position.x), int(nest.position.y)), int(nest.radius)
        )

    def _draw_ants(self, world: World) -> None:
        for ant in world.ants:
            color = _ANT_CARRYING if ant.has_food else _ANT_SEARCHING
            x, y = int(ant.position.x), int(ant.position.y)
            pygame.draw.circle(self.surface, color, (x, y), 3)
            if self.config.show_heading:
                end = ant.position + ant.heading * 7.0
                pygame.draw.line(self.surface, _HEADING_COLOR, (x, y), (int(end.x), int(end.y)), 1)

    def _draw_hud(self, world: World, fps: float) -> None:
        text = (
            f"Mrowki: {len(world.ants)}  |  Jedzenie w gniezdzie: {world.nest.food_stored}"
            f"  |  FPS: {fps:4.0f}"
        )
        surface = self.font.render(text, True, _TEXT_COLOR)
        self.surface.blit(surface, (10, 10))
