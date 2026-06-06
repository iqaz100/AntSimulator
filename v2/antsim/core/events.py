"""Minimalny dyspozytor zdarzeń (Observer).

Pozwala odseparować zbieranie statystyk od logiki symulacji: warstwa modelu
emituje nazwane zdarzenia (np. ``food_delivered``), a obserwatorzy reagują,
nie będąc znani symulacji.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Callable


class EventBus:
    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable[..., None]]] = defaultdict(list)

    def subscribe(self, event_name: str, callback: Callable[..., None]) -> None:
        self._listeners[event_name].append(callback)

    def emit(self, event_name: str, **payload) -> None:
        for callback in self._listeners.get(event_name, ()):
            callback(**payload)
