"""Mrówka — agent delegujący decyzje do bieżącego stanu (State pattern).

Sama mrówka odpowiada wyłącznie za *ruch fizyczny*: płynny obrót w stronę
pożądanego kierunku (z limitem prędkości skrętu) oraz całkowanie pozycji.
Logikę "co robić" trzyma obiekt stanu.
"""

from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

from antsim.core.vector import Vec2, wrap_to_pi

if TYPE_CHECKING:
    from antsim.behavior.states import AntState
    from antsim.core.world import World


class Ant:
    def __init__(self, position: Vec2, state: "AntState") -> None:
        self.position = position
        self.heading = Vec2.from_angle(random.uniform(0.0, 2.0 * math.pi))
        self.has_food = False
        self.time_since_goal = 0.0
        self.state = state

    def set_state(self, state: "AntState", world: "World") -> None:
        self.state = state
        state.on_enter(self, world)

    def update(self, world: "World", dt: float) -> None:
        self.state.update(self, world, dt)

    def move(self, desired_direction: Vec2, world: "World", dt: float) -> None:
        """Obraca heading ku ``desired_direction`` (z limitem) i przesuwa mrówkę."""
        cfg = world.config

        target_angle = desired_direction.angle()
        current_angle = self.heading.angle()
        diff = wrap_to_pi(target_angle - current_angle)

        max_step = cfg.ant_max_turn * dt
        diff = max(-max_step, min(max_step, diff))
        self.heading = Vec2.from_angle(current_angle + diff)

        step = self.heading * (cfg.ant_speed * dt)
        target = self.position + step
        clamped = Vec2(
            max(0.0, min(cfg.width, target.x)),
            max(0.0, min(cfg.height, target.y)),
        )
        self.position = self._resolve_obstacles(clamped, step, world)

    def _resolve_obstacles(self, target: Vec2, step: Vec2, world: "World") -> Vec2:
        """Nie pozwala wejść w przeszkodę; próbuje ślizgu po jednej osi."""
        if not world.point_in_obstacle(target):
            return target
        slide_x = Vec2(self.position.x + step.x, self.position.y)
        if not world.point_in_obstacle(slide_x):
            return slide_x
        slide_y = Vec2(self.position.x, self.position.y + step.y)
        if not world.point_in_obstacle(slide_y):
            return slide_y
        return self.position  # całkiem zablokowana — zostaje, kurs i tak się zmienia
