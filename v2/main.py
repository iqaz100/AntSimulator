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
from antsim.rendering.renderer import Renderer
from config.settings import SimulationConfig

_MAX_DT = 0.05  # zabezpieczenie przed skokiem czasu po zacięciu (s)


def run() -> None:
    config = SimulationConfig()

    pygame.init()
    screen = pygame.display.set_mode((config.width, config.height))
    pygame.display.set_caption("Symulator Mrówek v2")
    clock = pygame.time.Clock()

    simulation = Simulation(config)
    renderer = Renderer(screen, config)

    running = True
    while running:
        dt = min(clock.tick(config.fps) / 1000.0, _MAX_DT)
        running = _handle_events(config)
        simulation.step(dt)
        renderer.draw(simulation.world, clock.get_fps())
        pygame.display.flip()

    pygame.quit()


def _handle_events(config: SimulationConfig) -> bool:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            if event.key == pygame.K_p:
                config.show_pheromones = not config.show_pheromones
            elif event.key == pygame.K_h:
                config.show_heading = not config.show_heading
    return True


if __name__ == "__main__":
    run()
