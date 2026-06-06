# Symulator Mrówek — v2

Przepisana od zera wersja symulatora mrówek (Python + pygame + numpy) oparta na
algorytmie mrówkowym (ACO). Nacisk na czystą architekturę: separację warstw
model / widok / sterowanie, wzorce projektowe i testowalność.

> Stara wersja znajduje się w katalogu `../v1/` (zachowana jako referencja).

## Uruchomienie

```bash
cd v2
pip install -r requirements.txt
python main.py
```

Sterowanie:

| Klawisz | Działanie |
|---------|-----------|
| `ESC`   | Wyjście |
| `P`     | Pokaż / ukryj feromony |
| `H`     | Pokaż / ukryj wskaźnik kierunku mrówek |

## Jak działają mrówki

Każda mrówka to autonomiczny agent z **bezwładnością kierunku**: utrzymuje
aktualny kurs i obraca się płynnie, z ograniczeniem prędkości skrętu. Co klatkę
liczony jest **jeden** wektor pożądanego kierunku (złożenie składowych sterowania),
a kurs jest do niego interpolowany. To eliminuje „walkę o kąt" wielu systemów,
która w v1 powodowała kręcenie się w kółko.

Zachowanie opisuje **maszyna stanów**:

- **Szukanie** — mrówka szuka jedzenia, zostawia ślad „do domu" (HOME), węszy
  ślad „do jedzenia" (FOOD). Po znalezieniu jedzenia przełącza się w powrót.
- **Powrót** — mrówka niesie jedzenie, zostawia ślad „do jedzenia" (FOOD), węszy
  ślad „do domu" (HOME). Po oddaniu w gnieździe wraca do szukania.

Mrówka wykrywa feromon **trzema czujnikami** (lewo / środek / prawo) i skręca ku
najsilniejszemu sygnałowi. Siła zostawianego śladu maleje z czasem od ostatniego
celu — dzięki temu powstaje gradient prowadzący do źródła.

Feromony żyją na **siatce numpy** (dwie warstwy). Co krok parują (zanikają) i
opcjonalnie dyfundują (rozmycie).

## Architektura

```
main.py                  punkt wejścia: pętla + spięcie warstw
config/settings.py       SimulationConfig — jedyne źródło parametrów (DI)
antsim/
  core/
    vector.py            Vec2 — niezmienny wektor 2D (value object)
    events.py            EventBus — Observer
    world.py             World — agregat stanu (Aggregate Root)
    simulation.py        Simulation — krok modelu, bez pygame (testowalna)
  entities/              Ant, Nest, Food, Obstacle
  pheromones/grid.py     PheromoneGrid — numpy, parowanie + dyfuzja
  behavior/
    steering.py          składowe kierunku (Strategy)
    states.py            SearchingState / ReturningState (State)
  rendering/renderer.py  warstwa widoku (pygame)
  stats/collector.py     StatsCollector (Observer)
tests/                   testy logiki (vector, grid, steering, states)
experiments/benchmark.py powtarzalny pomiar wydajności (headless)
```

Zastosowane wzorce: **State** (zachowanie mrówki), **Strategy** (steering),
**Observer** (statystyki), **Aggregate Root** (World), **Dependency Injection**
(konfiguracja), value object (Vec2).

## Testy

```bash
cd v2
python run_tests.py        # wbudowany runner (bez zależności)
python -m pytest           # alternatywnie, jeśli masz pytest
```

## Badania / benchmark wydajności

Decyzje o parametrach (np. jak mocno mrówki mają trzymać się szlaków) opieram na
**pomiarach**, a nie na pojedynczej obserwacji „na oko". Służy do tego powtarzalny
skrypt `experiments/benchmark.py`. Działa *headless* — bez okna i bez pygame
(operuje na czystym modelu), więc liczy się szybko.

### Co i jak mierzy

Symulacja jest uruchamiana wielokrotnie, dla wielu ziaren losowych, i raportuje:

- **przepływ w stanie ustalonym** — ile jedzenia dostarczono na minutę w oknie
  `[warmup, duration]`, czyli *po* uformowaniu się szlaków feromonowych. To
  metryka odporna na szum. Sama „suma po N sekundach" jest myląca, bo zależy
  głównie od tego, jak szybko **pierwsza** mrówka przypadkiem trafi na jedzenie —
  ten losowy start potrafi zdominować krótki przebieg i maskować rzeczywisty efekt
  badanego parametru;
- **całość @duration** — łączne dostarczenia do końca przebiegu (zaszumione,
  podane dla porównania).

> Uwaga metodologiczna: pierwszy, pochopny pomiar (5 ziaren, „suma po 240 s")
> sugerował, że trzymanie się szlaków obniża wydajność. Dopiero rzetelna metryka
> (10 ziaren, stan ustalony) pokazała coś odwrotnego — dlatego ten skrypt domyślnie
> używa wielu ziaren i okna stanu ustalonego.

### Uruchomienie

```bash
cd v2
python -m experiments.benchmark                                   # domyślnie: trail_rejoin_chance = 0, 0.5, 1
python -m experiments.benchmark --param evaporation --values 0.05 0.12 0.25 --seeds 20
python -m experiments.benchmark --param ant_count --values 60 120 240 --duration 300
```

Parametry: `--param` (dowolne pole `SimulationConfig`), `--values` (lista wartości
do porównania), `--seeds`, `--duration`, `--warmup`.

### Przykładowy wynik (10 ziaren)

```
trail_rejoin_chance | przeplyw [dostarcz./min] | calosc @240s
------------------------------------------------------------
               0.0  |                   82.6  |          218.3
               0.5  |                  109.5  |          264.1
               1.0  |                  143.2  |          351.1
```

Wniosek: im chętniej mrówki wychodzą z gniazda istniejącym szlakiem
(`trail_rejoin_chance` → 1.0), tym wydajniejsza kolonia i wyraźniejsze szlaki —
stąd domyślna wartość `1.0`.

## Status / plan rozwoju

- [x] Etap 1 — fundament ruchu (bezwładność, płynne błądzenie)
- [x] Etap 2 — jedzenie i powrót (maszyna stanów)
- [x] Etap 3 — siatka feromonów (ACO: dwa ślady, parowanie, dyfuzja, czujniki)
- [ ] Etap 4 — przeszkody i interaktywna mapa (mysz)
- [ ] Etap 5 — panel sterowania na żywo (suwaki, przełączniki)
- [ ] Etap 6 — statystyki i wykresy w czasie
- [ ] Etap 7 — życie kolonii (głód, narodziny, drapieżniki)
- [ ] Etap 8 — wydajność, dopracowanie, dokumentacja
