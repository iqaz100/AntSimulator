from antsim.behavior.states import ReturningState, SearchingState
from antsim.core.vector import Vec2
from antsim.core.world import World
from antsim.entities.ant import Ant
from antsim.entities.food import Food
from config.settings import SimulationConfig


def make_world():
    cfg = SimulationConfig(width=400, height=400, food_source_count=0)
    return World(cfg), cfg


def test_searching_ant_picks_up_food_and_switches_state():
    world, cfg = make_world()
    food = Food(Vec2(100, 100), amount=10, radius=cfg.food_radius)
    world.foods.append(food)

    ant = Ant(Vec2(100, 100), SearchingState())
    world.ants.append(ant)

    delivered = []
    world.events.subscribe("food_picked", lambda **kw: delivered.append(kw))

    ant.update(world, dt=1.0 / 60.0)

    assert ant.has_food is True
    assert isinstance(ant.state, ReturningState)
    assert food.amount == 9
    assert len(delivered) == 1


def test_returning_ant_delivers_food_to_nest():
    world, cfg = make_world()
    ant = Ant(world.nest.position, ReturningState())
    ant.has_food = True
    world.ants.append(ant)

    events = []
    world.events.subscribe("food_delivered", lambda **kw: events.append(kw))

    ant.update(world, dt=1.0 / 60.0)

    assert ant.has_food is False
    assert isinstance(ant.state, SearchingState)
    assert world.nest.food_stored == 1
    assert len(events) == 1


def test_ant_moves_when_searching_without_food():
    world, _ = make_world()
    start = Vec2(200, 200)
    ant = Ant(start, SearchingState())
    world.ants.append(ant)

    ant.update(world, dt=1.0 / 60.0)

    assert ant.position != start
