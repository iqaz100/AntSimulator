"""Maszyna stanów zachowania mrówki (State pattern).

Stan wie tylko, *czego mrówka teraz szuka* i *jaki ślad zostawia*. Wspólna
logika (złożenie wektorów sterowania, depozyt feromonu, ruch) żyje w klasie
bazowej, więc poszczególne stany są krótkie i czytelne.

* ``SearchingState`` — szuka jedzenia, zostawia ślad HOME, węszy ślad FOOD.
* ``ReturningState`` — niesie jedzenie, zostawia ślad FOOD, węszy ślad HOME.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from antsim.behavior import steering
from antsim.core.vector import Vec2
from antsim.pheromones.grid import PheromoneGrid

if TYPE_CHECKING:
    from antsim.core.world import World
    from antsim.entities.ant import Ant


class AntState:
    """Bazowy stan — wspólny szkielet kroku mrówki."""

    deposit_layer: int = PheromoneGrid.HOME
    sense_layer: int = PheromoneGrid.FOOD

    def on_enter(self, ant: "Ant", world: "World") -> None:
        ant.time_since_goal = 0.0

    def update(self, ant: "Ant", world: "World", dt: float) -> None:
        raise NotImplementedError

    # --- Wspólne narzędzia dla podklas ---

    def _deposit_trail(self, ant: "Ant", world: "World") -> None:
        """Zostawia ślad, którego siła maleje z czasem od ostatniego celu.

        Daje to gradient: najsilniejszy ślad blisko źródła (gniazda/jedzenia).
        """
        cfg = world.config
        factor = max(0.0, 1.0 - ant.time_since_goal / cfg.deposit_decay_time)
        if factor <= 0.0:
            return
        world.pheromones.deposit(
            self.deposit_layer,
            ant.position.x,
            ant.position.y,
            cfg.deposit_amount * factor,
        )

    def _compose_direction(self, ant: "Ant", world: "World", seek_target: Vec2 | None) -> Vec2:
        """Składa składowe sterowania w jeden pożądany kierunek (znormalizowany)."""
        cfg = world.config
        desired = ant.heading * cfg.momentum_weight
        desired = desired + steering.wander(ant.heading) * cfg.wander_weight

        ph_dir, ph_strength = steering.follow_pheromone(
            world.pheromones, self.sense_layer, ant.position, ant.heading, cfg
        )
        if ph_strength > cfg.pheromone_sense_threshold:
            weight = cfg.pheromone_weight * min(1.0, ph_strength / cfg.deposit_max)
            desired = desired + ph_dir * weight

        if seek_target is not None:
            desired = desired + steering.seek(ant.position, seek_target) * cfg.seek_weight

        edge = steering.avoid_edges(ant.position, cfg.width, cfg.height, cfg.perception_radius)
        desired = desired + edge * cfg.avoid_weight

        result = desired.normalized()
        return result if result.length_sq() > 0.0 else ant.heading


class SearchingState(AntState):
    deposit_layer = PheromoneGrid.HOME
    sense_layer = PheromoneGrid.FOOD

    def on_enter(self, ant: "Ant", world: "World") -> None:
        super().on_enter(ant, world)
        # Wyjdź z gniazda — odwróć się od niego, by nie krążyć przy wejściu.
        away = (ant.position - world.nest.position).normalized()
        if away.length_sq() > 0.0:
            ant.heading = away

    def update(self, ant: "Ant", world: "World", dt: float) -> None:
        ant.time_since_goal += dt
        food = world.nearest_food(ant.position, world.config.perception_radius)

        if food is not None and food.contains(ant.position):
            food.take(1)
            ant.has_food = True
            world.events.emit("food_picked", ant=ant, food=food)
            ant.set_state(ReturningState(), world)
            return

        seek_target = food.position if food is not None else None
        desired = self._compose_direction(ant, world, seek_target)
        self._deposit_trail(ant, world)
        ant.move(desired, world, dt)


class ReturningState(AntState):
    deposit_layer = PheromoneGrid.FOOD
    sense_layer = PheromoneGrid.HOME

    def on_enter(self, ant: "Ant", world: "World") -> None:
        super().on_enter(ant, world)
        toward = (world.nest.position - ant.position).normalized()
        if toward.length_sq() > 0.0:
            ant.heading = toward

    def update(self, ant: "Ant", world: "World", dt: float) -> None:
        ant.time_since_goal += dt
        nest = world.nest

        if nest.contains(ant.position):
            nest.store_food(1)
            ant.has_food = False
            world.events.emit("food_delivered", ant=ant)
            ant.set_state(SearchingState(), world)
            return

        within_sight = ant.position.distance_to(nest.position) < world.config.perception_radius
        seek_target = nest.position if within_sight else None
        desired = self._compose_direction(ant, world, seek_target)
        self._deposit_trail(ant, world)
        ant.move(desired, world, dt)
