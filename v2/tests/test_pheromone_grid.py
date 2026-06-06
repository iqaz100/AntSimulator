from antsim.pheromones.grid import PheromoneGrid


def make_grid(evaporation=0.0, diffusion=0.0):
    return PheromoneGrid(
        width=100, height=100, cell_size=10,
        evaporation=evaporation, diffusion=diffusion, max_value=255.0,
    )


def test_deposit_and_sample():
    grid = make_grid()
    grid.deposit(PheromoneGrid.FOOD, 25, 25, 50.0)
    assert grid.sample(PheromoneGrid.FOOD, 25, 25) == 50.0
    assert grid.sample(PheromoneGrid.HOME, 25, 25) == 0.0


def test_deposit_clamped_to_max():
    grid = make_grid()
    grid.deposit(PheromoneGrid.FOOD, 5, 5, 1000.0)
    assert grid.sample(PheromoneGrid.FOOD, 5, 5) == 255.0


def test_sample_out_of_bounds_returns_zero():
    grid = make_grid()
    assert grid.sample(PheromoneGrid.FOOD, -10, -10) == 0.0
    assert grid.sample(PheromoneGrid.FOOD, 9999, 9999) == 0.0


def test_evaporation_reduces_value():
    grid = make_grid(evaporation=0.5)
    grid.deposit(PheromoneGrid.FOOD, 25, 25, 100.0)
    grid.update(dt=1.0)
    assert grid.sample(PheromoneGrid.FOOD, 25, 25) == 50.0


def test_diffusion_spreads_to_neighbors():
    grid = make_grid(diffusion=0.5)
    grid.deposit(PheromoneGrid.FOOD, 55, 55, 100.0)
    before_neighbor = grid.sample(PheromoneGrid.FOOD, 45, 55)
    grid.update(dt=1.0)
    after_neighbor = grid.sample(PheromoneGrid.FOOD, 45, 55)
    assert before_neighbor == 0.0
    assert after_neighbor > 0.0
