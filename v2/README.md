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

## Status / plan rozwoju

- [x] Etap 1 — fundament ruchu (bezwładność, płynne błądzenie)
- [x] Etap 2 — jedzenie i powrót (maszyna stanów)
- [x] Etap 3 — siatka feromonów (ACO: dwa ślady, parowanie, dyfuzja, czujniki)
- [ ] Etap 4 — przeszkody i interaktywna mapa (mysz)
- [ ] Etap 5 — panel sterowania na żywo (suwaki, przełączniki)
- [ ] Etap 6 — statystyki i wykresy w czasie
- [ ] Etap 7 — życie kolonii (głód, narodziny, drapieżniki)
- [ ] Etap 8 — wydajność, dopracowanie, dokumentacja
