"""Punkt wejścia symulatora mrówek (v2).

Spina warstwy: model (Simulation), widok (Renderer) i sterowanie (zdarzenia
pygame). Pętla używa kroku czasu opartego o realny dt, ograniczonego do FPS.

Uruchomienie:
    cd v2
    python main.py
"""

from __future__ import annotations

import os
import sys

# Pozwala uruchomić "python main.py" z katalogu v2 (pakiety: antsim, config).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame

from antsim.core.simulation import Simulation
from antsim.core.vector import Vec2
from antsim.rendering.charts import ChartPanel
from antsim.rendering.renderer import Renderer
from antsim.rendering.ui import ControlPanel
from config.settings import SimulationConfig

_MAX_DT = 0.05  # zabezpieczenie przed skokiem czasu po zacięciu (s)
_ANTS_PER_KEYPRESS = 20


def run() -> None:
    config = SimulationConfig()

    pygame.init()
    screen = pygame.display.set_mode((config.width, config.height))
    pygame.display.set_caption("Symulator Mrówek v2")
    clock = pygame.time.Clock()

    simulation = Simulation(config)
    renderer = Renderer(screen, config)
    panel = ControlPanel(simulation, config)
    charts = ChartPanel(simulation.stats, config)

    running = True
    while running:
        dt = min(clock.tick(config.fps) / 1000.0, _MAX_DT)
        running = _handle_events(simulation, config, panel)
        _handle_mouse_paint(simulation, panel)
        simulation.step(dt)
        renderer.draw(simulation.world, clock.get_fps())
        charts.draw(screen)
        panel.draw(screen)
        pygame.display.flip()

    pygame.quit()


def _handle_events(simulation: Simulation, config: SimulationConfig, panel: ControlPanel) -> bool:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if panel.handle_event(event):   # panel ma pierwszeństwo nad światem
            continue
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            if event.key == pygame.K_p:
                config.show_pheromones = not config.show_pheromones
            elif event.key == pygame.K_h:
                config.show_heading = not config.show_heading
            elif event.key == pygame.K_TAB:
                panel.visible = not panel.visible
            elif event.key == pygame.K_s:
                config.show_charts = not config.show_charts
            elif event.key == pygame.K_SPACE:
                simulation.add_ants(_ANTS_PER_KEYPRESS)
            elif event.key == pygame.K_r:
                simulation.clear_obstacles()
            elif event.key == pygame.K_c:
                simulation.clear_pheromones()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            position = Vec2(*event.pos)
            if event.button == 1:        # LPM — postaw jedzenie
                simulation.add_food_at(position)
            elif event.button == 3:      # PPM — postaw przeszkodę
                simulation.add_obstacle_at(position)
    return True


def _handle_mouse_paint(simulation: Simulation, panel: ControlPanel) -> None:
    """Trzymanie PPM maluje ciąg przeszkód (wygodne rysowanie ścian)."""
    if pygame.mouse.get_pressed()[2] and not panel.wants_mouse(pygame.mouse.get_pos()):
        simulation.add_obstacle_at(Vec2(*pygame.mouse.get_pos()))


if __name__ == "__main__":
    run()
