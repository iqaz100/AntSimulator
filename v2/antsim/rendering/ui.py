"""Panel sterowania na żywo (warstwa widoku/sterowania UI).

Minimalny zestaw widżetów (suwak, przełącznik) w stylu immediate-mode. Każdy
widżet wiąże się z wartością przez parę getter/setter, więc UI nie zna struktury
modelu — po prostu czyta i zapisuje wskazane pola (konfiguracji lub siatki
feromonów). Panel przechwytuje zdarzenia myszy nad swoim obszarem, by klik w
suwak nie stawiał jednocześnie jedzenia/przeszkody w świecie.
"""

from __future__ import annotations

from typing import Callable

import pygame

_PANEL_BG = (26, 26, 32)
_PANEL_BORDER = (70, 70, 82)
_TRACK = (66, 66, 78)
_HANDLE = (205, 205, 215)
_TEXT = (224, 224, 230)
_TOGGLE_ON = (110, 200, 120)
_TOGGLE_OFF = (84, 84, 96)


class Slider:
    """Suwak liczbowy wiązany przez getter/setter."""

    def __init__(self, rect: pygame.Rect, label: str,
                 getter: Callable[[], float], setter: Callable[[float], None],
                 minimum: float, maximum: float, fmt: str = "{:.2f}") -> None:
        self.rect = rect
        self.label = label
        self.getter = getter
        self.setter = setter
        self.minimum = minimum
        self.maximum = maximum
        self.fmt = fmt
        self._dragging = False

    def _track(self) -> pygame.Rect:
        return pygame.Rect(self.rect.x + 8, self.rect.y + 22, self.rect.width - 16, 6)

    def _value_to_x(self, track: pygame.Rect) -> int:
        span = self.maximum - self.minimum
        ratio = 0.0 if span == 0 else (self.getter() - self.minimum) / span
        ratio = max(0.0, min(1.0, ratio))
        return track.x + int(ratio * track.width)

    def _x_to_value(self, x: int, track: pygame.Rect) -> float:
        ratio = (x - track.x) / track.width if track.width else 0.0
        ratio = max(0.0, min(1.0, ratio))
        return self.minimum + ratio * (self.maximum - self.minimum)

    def handle_event(self, event: pygame.event.Event) -> bool:
        track = self._track()
        hot = pygame.Rect(track.x - 6, track.y - 12, track.width + 12, track.height + 24)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and hot.collidepoint(event.pos):
            self._dragging = True
            self.setter(self._x_to_value(event.pos[0], track))
            return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self._dragging:
            self._dragging = False
            return True
        if event.type == pygame.MOUSEMOTION and self._dragging:
            self.setter(self._x_to_value(event.pos[0], track))
            return True
        return False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        label = f"{self.label}: {self.fmt.format(self.getter())}"
        surface.blit(font.render(label, True, _TEXT), (self.rect.x + 6, self.rect.y + 2))
        track = self._track()
        pygame.draw.rect(surface, _TRACK, track, border_radius=3)
        handle_x = self._value_to_x(track)
        pygame.draw.circle(surface, _HANDLE, (handle_x, track.y + track.height // 2), 7)


class Toggle:
    """Przełącznik bool wiązany przez getter/setter."""

    def __init__(self, rect: pygame.Rect, label: str,
                 getter: Callable[[], bool], setter: Callable[[bool], None]) -> None:
        self.rect = rect
        self.label = label
        self.getter = getter
        self.setter = setter

    def _box(self) -> pygame.Rect:
        return pygame.Rect(self.rect.x + 6, self.rect.y + 3, 18, 18)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.setter(not self.getter())
            return True
        return False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        box = self._box()
        color = _TOGGLE_ON if self.getter() else _TOGGLE_OFF
        pygame.draw.rect(surface, color, box, border_radius=4)
        surface.blit(font.render(self.label, True, _TEXT), (box.right + 8, self.rect.y + 2))


class ControlPanel:
    """Składa widżety, rozkłada je w pionie i obsługuje zdarzenia/rysowanie."""

    WIDTH = 248
    ROW = 40
    PAD = 12

    def __init__(self, simulation, config) -> None:
        self.simulation = simulation
        self.config = config
        self.visible = True
        self.font = pygame.font.Font(None, 22)
        self.widgets: list = []
        self._build()

    def _build(self) -> None:
        cfg = self.config
        sim = self.simulation
        world = sim.world
        grid = world.pheromones

        x = cfg.width - self.WIDTH - self.PAD
        self._top = 44
        y = self._top + 6

        def slider(label, getter, setter, lo, hi, fmt="{:.2f}") -> None:
            nonlocal y
            self.widgets.append(
                Slider(pygame.Rect(x, y, self.WIDTH, self.ROW - 8), label, getter, setter, lo, hi, fmt)
            )
            y += self.ROW

        def toggle(label, getter, setter) -> None:
            nonlocal y
            self.widgets.append(Toggle(pygame.Rect(x, y, self.WIDTH, 26), label, getter, setter))
            y += 28

        slider("Mrowki", lambda: len(world.ants), lambda v: sim.set_population(int(v)), 0, 400, "{:.0f}")
        slider("Predkosc", lambda: cfg.ant_speed, lambda v: setattr(cfg, "ant_speed", v), 10, 140, "{:.0f}")
        slider("Parowanie", lambda: grid.evaporation, lambda v: setattr(grid, "evaporation", v), 0.0, 0.5)
        slider("Dyfuzja", lambda: grid.diffusion, lambda v: setattr(grid, "diffusion", v), 0.0, 0.3)
        slider("Sila feromonu", lambda: cfg.deposit_amount, lambda v: setattr(cfg, "deposit_amount", v), 0, 255, "{:.0f}")
        slider("Waga feromonu", lambda: cfg.pheromone_weight, lambda v: setattr(cfg, "pheromone_weight", v), 0.0, 3.0)
        slider("Trzymanie szlaku", lambda: cfg.trail_rejoin_chance, lambda v: setattr(cfg, "trail_rejoin_chance", v), 0.0, 1.0)
        toggle("Feromony (P)", lambda: cfg.show_pheromones, lambda b: setattr(cfg, "show_pheromones", b))
        toggle("Kierunek (H)", lambda: cfg.show_heading, lambda b: setattr(cfg, "show_heading", b))

        self._x = x
        self._bottom = y

    def panel_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self._x - self.PAD,
            self._top - self.PAD,
            self.WIDTH + 2 * self.PAD,
            (self._bottom - self._top) + 2 * self.PAD,
        )

    def wants_mouse(self, position: tuple[int, int]) -> bool:
        """Czy mysz powinna być obsłużona przez panel (a nie przez świat)."""
        if not self.visible:
            return False
        if any(getattr(w, "_dragging", False) for w in self.widgets):
            return True
        return self.panel_rect().collidepoint(position)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False
        for widget in self.widgets:
            if widget.handle_event(event):
                return True
        # Pochłoń pozostałe kliknięcia w obrębie panelu (np. w tło).
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP) and \
                self.panel_rect().collidepoint(event.pos):
            return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        rect = self.panel_rect()
        pygame.draw.rect(surface, _PANEL_BG, rect, border_radius=6)
        pygame.draw.rect(surface, _PANEL_BORDER, rect, 1, border_radius=6)
        for widget in self.widgets:
            widget.draw(surface, self.font)
