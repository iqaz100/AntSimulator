import pygame

from antsim.core.simulation import Simulation
from antsim.rendering.ui import Slider, Toggle
from config.settings import SimulationConfig


def test_set_population_grows_and_shrinks():
    sim = Simulation(SimulationConfig(ant_count=50, food_source_count=0), seed=1)
    assert len(sim.world.ants) == 50
    sim.set_population(80)
    assert len(sim.world.ants) == 80
    sim.set_population(30)
    assert len(sim.world.ants) == 30
    sim.set_population(-5)
    assert len(sim.world.ants) == 0


def test_slider_maps_position_to_value():
    store = {"v": 0.0}
    slider = Slider(
        pygame.Rect(100, 0, 200, 32), "x",
        getter=lambda: store["v"], setter=lambda v: store.__setitem__("v", v),
        minimum=0.0, maximum=10.0,
    )
    track = slider._track()
    # Kliknięcie w środek toru -> ~połowa zakresu.
    middle = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                                pos=(track.x + track.width // 2, track.y))
    assert slider.handle_event(middle) is True
    assert abs(store["v"] - 5.0) < 0.6


def test_slider_clamps_below_minimum():
    store = {"v": 5.0}
    slider = Slider(
        pygame.Rect(100, 0, 200, 32), "x",
        getter=lambda: store["v"], setter=lambda v: store.__setitem__("v", v),
        minimum=0.0, maximum=10.0,
    )
    track = slider._track()
    # Klik tuż przy lewej krawędzi strefy aktywnej (na lewo od toru) -> minimum.
    left_edge = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(track.x - 5, track.y))
    assert slider.handle_event(left_edge) is True
    assert store["v"] == 0.0


def test_toggle_flips_on_click():
    store = {"on": False}
    toggle = Toggle(
        pygame.Rect(0, 0, 200, 26), "t",
        getter=lambda: store["on"], setter=lambda b: store.__setitem__("on", b),
    )
    click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(10, 10))
    assert toggle.handle_event(click) is True
    assert store["on"] is True
    # Klik poza obszarem nie przełącza.
    outside = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(500, 500))
    assert toggle.handle_event(outside) is False
    assert store["on"] is True
