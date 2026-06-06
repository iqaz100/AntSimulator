from antsim.core.events import EventBus
from antsim.stats.collector import StatsCollector


class FakeWorld:
    def __init__(self, population):
        self.ants = list(range(population))


def test_counts_food_delivered_events():
    events = EventBus()
    stats = StatsCollector(events)
    for _ in range(3):
        events.emit("food_delivered")
    assert stats.food_delivered == 3


def test_sampling_records_rate_and_population():
    events = EventBus()
    stats = StatsCollector(events, sample_interval=1.0)
    world = FakeWorld(population=10)

    # 6 dostarczeń w ciągu 1 s -> 360 / min.
    for _ in range(6):
        events.emit("food_delivered")
    for _ in range(60):
        stats.tick(1.0 / 60.0, world)

    assert len(stats.history) == 1
    sample = stats.history[-1]
    assert abs(sample.rate_per_min - 360.0) < 1e-6
    assert sample.population == 10
    assert sample.cumulative_food == 6
    assert abs(sample.efficiency - 36.0) < 1e-6


def test_history_is_bounded():
    events = EventBus()
    stats = StatsCollector(events, sample_interval=0.1, history_size=5)
    world = FakeWorld(population=1)
    for _ in range(300):  # 30 s przy interwale 0.1 s -> 300 próbek, ale limit 5
        stats.tick(0.1, world)
    assert len(stats.history) == 5


def test_no_sample_before_interval():
    events = EventBus()
    stats = StatsCollector(events, sample_interval=1.0)
    world = FakeWorld(population=4)
    for _ in range(30):  # 0.5 s
        stats.tick(1.0 / 60.0, world)
    assert len(stats.history) == 0
