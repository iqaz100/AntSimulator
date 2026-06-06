import math

from antsim.behavior import steering
from antsim.core.simulation import Simulation
from antsim.core.vector import Vec2
from antsim.core.world import World
from antsim.entities.ant import Ant
from antsim.entities.obstacle import Obstacle
from antsim.behavior.states import SearchingState
from config.settings import SimulationConfig


def test_obstacle_contains_and_closest_point():
    obstacle = Obstacle(100, 100, 50, 50)
    assert obstacle.contains(Vec2(125, 125)) is True
    assert obstacle.contains(Vec2(10, 10)) is False
    # Punkt na lewo od prostokąta -> najbliższy punkt na lewej krawędzi.
    closest = obstacle.closest_point(Vec2(80, 125))
    assert closest == Vec2(100, 125)


def test_avoid_obstacles_pushes_away_from_surface():
    obstacle = Obstacle(100, 100, 50, 50)
    # Mrówka tuż po lewej stronie przeszkody -> wektor powinien pchać w lewo (-x).
    push = steering.avoid_obstacles(Vec2(95, 125), [obstacle], lookahead=28.0)
    assert push.x < 0
    assert abs(push.y) < abs(push.x)


def test_avoid_obstacles_zero_when_far():
    obstacle = Obstacle(100, 100, 50, 50)
    assert steering.avoid_obstacles(Vec2(10, 10), [obstacle], lookahead=28.0) == Vec2(0, 0)


def test_world_point_in_obstacle():
    world = World(SimulationConfig(width=400, height=400, food_source_count=0))
    world.obstacles.append(Obstacle(100, 100, 50, 50))
    assert world.point_in_obstacle(Vec2(125, 125)) is True
    assert world.point_in_obstacle(Vec2(0, 0)) is False


def test_ant_does_not_enter_obstacle():
    cfg = SimulationConfig(width=400, height=400, food_source_count=0, ant_speed=200.0)
    world = World(cfg)
    obstacle = Obstacle(100, 100, 80, 80)
    world.obstacles.append(obstacle)

    ant = Ant(Vec2(90, 140), SearchingState())
    ant.heading = Vec2(1, 0)  # prosto w stronę przeszkody
    world.ants.append(ant)

    for _ in range(30):
        ant.update(world, dt=1.0 / 60.0)
        assert not obstacle.contains(ant.position)


def test_simulation_add_obstacle_skips_duplicate_and_nest():
    sim = Simulation(SimulationConfig(width=600, height=600, food_source_count=0), seed=1)
    nest = sim.world.nest
    sim.add_obstacle_at(nest.position)  # na gnieździe -> pominięte
    assert len(sim.world.obstacles) == 0

    spot = Vec2(50, 50)
    sim.add_obstacle_at(spot)
    sim.add_obstacle_at(spot)  # ten sam punkt -> brak duplikatu
    assert len(sim.world.obstacles) == 1
