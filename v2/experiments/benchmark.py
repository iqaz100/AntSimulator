"""Benchmark kolonii — powtarzalny pomiar wydajności symulacji.

Uruchamia symulację *headless* (bez okna, bez pygame) na wielu ziarnach losowych
i mierzy dwie wielkości:

* **przepływ w stanie ustalonym** — ile jedzenia dostarczono na minutę w oknie
  ``[warmup, duration]`` (po tym jak szlaki feromonowe zdążą się uformować).
  To metryka odporna na szum, bo pomija losowy początek (kiedy *pierwsza* mrówka
  przypadkiem trafi na jedzenie, co potrafi zdominować krótki przebieg);
* **całość @duration** — łączna liczba dostarczeń do końca przebiegu (bardziej
  zaszumiona, podana dla porównania).

Można porównać kilka wartości dowolnego parametru z ``SimulationConfig`` (sweep),
np. wpływ ``trail_rejoin_chance`` na wydajność.

Przykłady:
    cd v2
    python -m experiments.benchmark
    python -m experiments.benchmark --param trail_rejoin_chance --values 0 0.5 1
    python -m experiments.benchmark --param evaporation --values 0.05 0.12 0.25 --seeds 20
    python -m experiments.benchmark --param ant_count --values 60 120 240 --duration 300
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import replace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from antsim.core.simulation import Simulation
from config.settings import SimulationConfig

DT = 1.0 / 60.0


def run_once(config: SimulationConfig, seed: int, warmup: float, duration: float) -> tuple[float, int]:
    """Zwraca (dostarczenia/min w oknie [warmup, duration], całość @duration)."""
    sim = Simulation(config, seed=seed)
    while sim.stats.elapsed_time < warmup:
        sim.step(DT)
    delivered_at_warmup = sim.stats.food_delivered
    while sim.stats.elapsed_time < duration:
        sim.step(DT)

    window_minutes = (duration - warmup) / 60.0
    steady_per_min = (sim.stats.food_delivered - delivered_at_warmup) / window_minutes
    return steady_per_min, sim.stats.food_delivered


def _coerce(reference, raw: str):
    """Rzutuje napis z CLI na typ zgodny z domyślną wartością pola konfiguracji."""
    if isinstance(reference, bool):
        return raw.lower() in ("1", "true", "tak", "yes", "on")
    if isinstance(reference, int):
        return int(raw)
    if isinstance(reference, float):
        return float(raw)
    return raw


def main() -> None:
    defaults = SimulationConfig()
    parser = argparse.ArgumentParser(description="Benchmark wydajności kolonii mrówek")
    parser.add_argument("--param", default="trail_rejoin_chance",
                        help="nazwa pola SimulationConfig do porównania (sweep)")
    parser.add_argument("--values", nargs="*", default=["0.0", "0.5", "1.0"],
                        help="wartości parametru do porównania")
    parser.add_argument("--seeds", type=int, default=10,
                        help="liczba ziaren losowych (uśrednianie)")
    parser.add_argument("--duration", type=float, default=240.0,
                        help="długość przebiegu w sekundach symulacji")
    parser.add_argument("--warmup", type=float, default=120.0,
                        help="początek okna pomiaru stanu ustalonego [s]")
    args = parser.parse_args()

    if not hasattr(defaults, args.param):
        parser.error(f"SimulationConfig nie ma pola '{args.param}'")

    seeds = list(range(1, args.seeds + 1))
    reference = getattr(defaults, args.param)

    print(f"Parametr: {args.param}   ziarna: {args.seeds}   "
          f"okno stanu ustalonego: {args.warmup:.0f}-{args.duration:.0f}s\n")
    header = f"{args.param:>18} | przeplyw [dostarcz./min] | calosc @{args.duration:.0f}s"
    print(header)
    print("-" * len(header))

    for raw in args.values:
        value = _coerce(reference, raw)
        config = replace(defaults, **{args.param: value})
        steady_runs = []
        total_runs = []
        for seed in seeds:
            steady, total = run_once(config, seed, args.warmup, args.duration)
            steady_runs.append(steady)
            total_runs.append(total)
        avg_steady = sum(steady_runs) / len(steady_runs)
        avg_total = sum(total_runs) / len(total_runs)
        print(f"{str(value):>18} | {avg_steady:21.1f} | {avg_total:14.1f}")


if __name__ == "__main__":
    main()
