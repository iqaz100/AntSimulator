import math

from antsim.behavior import steering
from antsim.core.vector import Vec2
from antsim.pheromones.grid import PheromoneGrid
from config.settings import SimulationConfig


def test_seek_points_at_target():
    direction = steering.seek(Vec2(0, 0), Vec2(10, 0))
    assert math.isclose(direction.x, 1.0)
    assert math.isclose(direction.y, 0.0)


def test_avoid_edges_pushes_inward():
    cfg = SimulationConfig()
    push = steering.avoid_edges(Vec2(1, 1), cfg.width, cfg.height, margin=40)
    assert push.x > 0 and push.y > 0
    no_push = steering.avoid_edges(Vec2(600, 400), cfg.width, cfg.height, margin=40)
    assert no_push == Vec2(0, 0)


def test_follow_pheromone_turns_toward_stronger_side():
    cfg = SimulationConfig()
    grid = PheromoneGrid(400, 400, 4, evaporation=0.0, diffusion=0.0, max_value=255.0)
    position = Vec2(200, 200)
    heading = Vec2(1, 0)  # patrzy w prawo (+x)

    # Ślad po lewej stronie mrówki (czujnik obrócony o +sensor_angle).
    left_dir = heading.rotated(cfg.sensor_angle)
    left_point = position + left_dir * cfg.sensor_distance
    grid.deposit(PheromoneGrid.FOOD, left_point.x, left_point.y, 200.0)

    direction, strength = steering.follow_pheromone(
        grid, PheromoneGrid.FOOD, position, heading, cfg
    )
    assert strength > 0
    assert math.isclose(direction.angle(), left_dir.angle(), abs_tol=1e-6)


def test_follow_pheromone_no_trail_keeps_heading():
    cfg = SimulationConfig()
    grid = PheromoneGrid(400, 400, 4, evaporation=0.0, diffusion=0.0, max_value=255.0)
    heading = Vec2(0, 1)
    direction, strength = steering.follow_pheromone(
        grid, PheromoneGrid.FOOD, Vec2(200, 200), heading, cfg
    )
    assert strength == 0.0
    assert direction == heading
