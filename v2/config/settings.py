"""Konfiguracja symulacji.

Pojedyncze, jawne źródło parametrów (zastępuje rozsypane stałe globalne z v1).
Obiekt jest wstrzykiwany do symulacji, świata i zachowań (Dependency Injection),
dzięki czemu nic nie sięga po stan globalny.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SimulationConfig:
    """Wszystkie nastawy symulacji wraz z wartościami domyślnymi.

    Pola są pogrupowane tematycznie. Wartości można nadpisać przy tworzeniu
    obiektu lub zmieniać w trakcie działania (panel sterowania — Etap 5).
    """

    # --- Okno / pętla ---
    width: int = 1200
    height: int = 800
    fps: int = 60

    # --- Kolonia ---
    ant_count: int = 120
    nest_radius: float = 26.0

    # --- Ruch mrówki ---
    ant_speed: float = 55.0          # px/s
    ant_max_turn: float = 7.0        # maksymalna prędkość skrętu [rad/s]
    perception_radius: float = 36.0  # zasięg "wzroku" (jedzenie, gniazdo)

    # Wagi składowych pożądanego kierunku (steering).
    # Wszystkie składane w JEDEN wektor na klatkę -> brak "walki o kąt" jak w v1.
    momentum_weight: float = 1.0     # bezwładność (utrzymanie kierunku)
    wander_weight: float = 0.18      # losowy szum błądzenia
    pheromone_weight: float = 1.6    # podążanie za feromonem
    seek_weight: float = 3.2         # dojście do widocznego celu
    avoid_weight: float = 4.5        # omijanie krawędzi / przeszkód

    # --- Sensory feromonowe (3 czujniki: lewo / środek / prawo) ---
    sensor_angle: float = 0.6        # rozstaw czujników bocznych [rad]
    sensor_distance: float = 22.0    # jak daleko przed mrówką próbkujemy [px]
    pheromone_sense_threshold: float = 0.05  # poniżej tej wartości ignorujemy ślad

    # Szansa, że mrówka wychodząca z gniazda od razu wejdzie na istniejący szlak
    # FOOD (reszta rusza promieniście). Mechanizm jest samoregulujący: gdy szlaku
    # nie ma (wczesna faza), mrówka i tak rusza promieniście i eksploruje.
    # Pomiar (10 seedów, przepływ w stanie ustalonym): 0.0->83/min, 0.5->110/min,
    # 1.0->143/min — wyższa wartość = wydajniejsza kolonia i wyraźniejsze szlaki.
    trail_rejoin_chance: float = 1.0

    # --- Siatka feromonów ---
    cell_size: int = 4               # rozmiar komórki siatki [px]
    evaporation: float = 0.12        # frakcja odparowania na sekundę
    diffusion: float = 0.04          # współczynnik rozmycia na sekundę (0 = brak)
    deposit_amount: float = 220.0    # siła świeżego depozytu
    deposit_max: float = 255.0       # górne ograniczenie (mapuje się na kolor)
    deposit_decay_time: float = 28.0 # po tylu s od "celu" depozyt spada do zera

    # --- Przeszkody ---
    obstacle_avoid_lookahead: float = 28.0  # zasięg wykrywania przeszkody [px]
    obstacle_place_size: float = 56.0       # bok przeszkody stawianej myszką [px]

    # --- Jedzenie ---
    food_source_count: int = 3
    food_amount: int = 1200
    food_radius: float = 34.0
    food_min_distance_from_nest: float = 240.0

    # --- Statystyki ---
    stats_sample_interval: float = 1.0  # co ile sekund zapisać próbkę do historii
    stats_history_size: int = 240       # ile próbek trzymać (okno wykresów)

    # --- Render ---
    show_pheromones: bool = True
    show_heading: bool = True
    show_charts: bool = True
    background_color: tuple[int, int, int] = (18, 18, 22)
