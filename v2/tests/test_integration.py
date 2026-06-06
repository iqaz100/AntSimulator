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


def test_resize_adjusts_world_and_preserves_trails():
    from antsim.pheromones.grid import PheromoneGrid

    cfg = SimulationConfig(width=400, height=400, ant_count=20, food_source_count=0)
    sim = Simulation(cfg, seed=1)
    sim.world.pheromones.deposit(PheromoneGrid.FOOD, 50, 50, 200.0)

    sim.resize(800, 600)

    assert cfg.width == 800 and cfg.height == 600
    assert sim.world.pheromones.cols == 800 // cfg.cell_size
    assert sim.world.pheromones.rows == 600 // cfg.cell_size
    # Ślad z nakładającego się obszaru przetrwał zmianę rozmiaru.
    assert sim.world.pheromones.sample(PheromoneGrid.FOOD, 50, 50) == 200.0
    for ant in sim.world.ants:
        assert 0.0 <= ant.position.x <= 800
        assert 0.0 <= ant.position.y <= 600


def test_resize_clamps_entities_when_shrinking():
    cfg = SimulationConfig(width=800, height=800, ant_count=30, food_source_count=0)
    sim = Simulation(cfg, seed=1)
    sim.resize(300, 300)
    for ant in sim.world.ants:
        assert 0.0 <= ant.position.x <= 300
        assert 0.0 <= ant.position.y <= 300
    assert 0.0 <= sim.world.nest.position.x <= 300


def test_invalid_config_raises():
    for kwargs in ({"width": 0}, {"cell_size": 0}, {"ant_count": -1}, {"trail_rejoin_chance": 1.5}):
        try:
            SimulationConfig(**kwargs)
        except ValueError:
            continue
        raise AssertionError(f"Oczekiwano ValueError dla {kwargs}")
