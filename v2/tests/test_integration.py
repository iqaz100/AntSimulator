"""Testy integracyjne — pełna symulacja (model) bez okna i renderu."""

from antsim.core.simulation import Simulation
from antsim.core.vector import Vec2
from config.settings import SimulationConfig


def test_simulation_runs_and_keeps_invariants():
    cfg = SimulationConfig(width=500, height=500, ant_count=40)
    sim = Simulation(cfg, seed=3)
    sim.add_obstacle_at(Vec2(250, 250))

    for _ in range(300):  # 5 s symulacji
        sim.step(1.0 / 60.0)

    assert len(sim.world.ants) == 40
    for ant in sim.world.ants:
        assert 0.0 <= ant.position.x <= cfg.width
        assert 0.0 <= ant.position.y <= cfg.height
        assert not sim.world.point_in_obstacle(ant.position)


def test_depleted_food_is_removed():
    cfg = SimulationConfig(width=400, height=400, ant_count=0, food_source_count=0)
    sim = Simulation(cfg, seed=1)
    sim.add_food_at(Vec2(100, 100))
    sim.world.foods[0].take(sim.world.foods[0].amount)  # opróżnij
    sim.step(1.0 / 60.0)
    assert len(sim.world.foods) == 0


def test_food_delivery_happens_over_time():
    sim = Simulation(SimulationConfig(), seed=2)
    for _ in range(60 * 60):  # 60 s
        sim.step(1.0 / 60.0)
    assert sim.stats.food_delivered > 0


def test_invalid_config_raises():
    for kwargs in ({"width": 0}, {"cell_size": 0}, {"ant_count": -1}, {"trail_rejoin_chance": 1.5}):
        try:
            SimulationConfig(**kwargs)
        except ValueError:
            continue
        raise AssertionError(f"Oczekiwano ValueError dla {kwargs}")
