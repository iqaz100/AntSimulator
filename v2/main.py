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
    screen = pygame.display.set_mode((config.width, config.height), pygame.RESIZABLE)
    pygame.display.set_caption("Symulator Mrówek v2")
    clock = pygame.time.Clock()

    simulation = Simulation(config)
    renderer = Renderer(screen, config)
    panel = ControlPanel(simulation, config)
    charts = ChartPanel(simulation.stats, config)

    fullscreen = False
    windowed_size = (config.width, config.height)

    running = True
    while running:
        dt = min(clock.tick(config.fps) / 1000.0, _MAX_DT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if panel.handle_event(event):   # panel ma pierwszeństwo nad światem
                continue
            if event.type == pygame.VIDEORESIZE and not fullscreen:
                windowed_size = event.size
                screen, panel = _set_display(simulation, renderer, panel, event.size, pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        windowed_size = (config.width, config.height)
                        info = pygame.display.Info()
                        size, flags = (info.current_w, info.current_h), pygame.FULLSCREEN
                    else:
                        size, flags = windowed_size, pygame.RESIZABLE
                    screen, panel = _set_display(simulation, renderer, panel, size, flags)
                else:
                    _handle_sim_key(event, simulation, config, panel)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                _handle_world_mouse(event, simulation)

        _handle_mouse_paint(simulation, panel)
        simulation.step(dt)
        renderer.draw(simulation.world, clock.get_fps())
        charts.draw(screen)
        panel.draw(screen)
        pygame.display.flip()

    pygame.quit()


def _set_display(simulation: Simulation, renderer: Renderer, panel: ControlPanel,
                 size: tuple[int, int], flags: int) -> tuple[pygame.Surface, ControlPanel]:
    """Zmienia tryb wyświetlania i dopasowuje świat oraz panel do nowego rozmiaru."""
    screen = pygame.display.set_mode(size, flags)
    simulation.resize(size[0], size[1])
    renderer.surface = screen
    new_panel = ControlPanel(simulation, simulation.config)  # przelicza pozycje na nowy rozmiar
    new_panel.visible = panel.visible
    return screen, new_panel


def _handle_sim_key(event: pygame.event.Event, simulation: Simulation,
                    config: SimulationConfig, panel: ControlPanel) -> None:
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


def _handle_world_mouse(event: pygame.event.Event, simulation: Simulation) -> None:
    position = Vec2(*event.pos)
    if event.button == 1:        # LPM — postaw jedzenie
        simulation.add_food_at(position)
    elif event.button == 3:      # PPM — postaw przeszkodę
        simulation.add_obstacle_at(position)


def _handle_mouse_paint(simulation: Simulation, panel: ControlPanel) -> None:
    """Trzymanie PPM maluje ciąg przeszkód (wygodne rysowanie ścian)."""
    if pygame.mouse.get_pressed()[2] and not panel.wants_mouse(pygame.mouse.get_pos()):
        simulation.add_obstacle_at(Vec2(*pygame.mouse.get_pos()))


if __name__ == "__main__":
    run()
