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

Okno jest skalowalne (można je maksymalizować jak zwykłe okno) — `F11` przełącza
pełny ekran. Po zmianie rozmiaru świat dopasowuje się do nowych wymiarów.

Sterowanie:

| Klawisz / mysz | Działanie |
|----------------|-----------|
| `ESC`          | Wyjście |
| `F11`          | Pełny ekran / powrót do okna |
| `P`            | Pokaż / ukryj feromony |
| `H`            | Pokaż / ukryj wskaźnik kierunku mrówek |
| `TAB`          | Pokaż / ukryj panel sterowania |
| `S`            | Pokaż / ukryj wykresy |
| `SPACJA`       | Dodaj mrówki |
| `R`            | Usuń wszystkie przeszkody |
| `C`            | Wyczyść feromony |
| **LPM**        | Postaw źródło jedzenia |
| **PPM**        | Postaw przeszkodę (przytrzymaj, by malować ścianę) |

Panel sterowania (prawy górny róg, `TAB` chowa) pozwala zmieniać na żywo: liczbę
mrówek, prędkość, parowanie i dyfuzję feromonów, siłę i wagę feromonu oraz
„trzymanie szlaku", a także przełączać warstwy feromonów i wskaźnik kierunku.

Wykresy w czasie (lewy dolny róg, `S` chowa) pokazują: tempo dostarczeń na minutę,
liczebność kolonii, łączną ilość zebranego jedzenia oraz wydajność na mrówkę.

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
  rendering/
    renderer.py          warstwa widoku (pygame)
    ui.py                panel sterowania na żywo (suwaki, przełączniki)
    charts.py            wykresy szeregów czasowych
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

37 testów pokrywa czystą logikę: wektory, siatkę feromonów, steering, maszynę
stanów, przeszkody, UI, statystyki oraz przebieg integracyjny (niezmienniki:
mrówki w granicach planszy i poza przeszkodami).

## Wydajność

Symulacja i render są rozdzielone; model jest tani, a koszt rośnie liniowo z
liczbą mrówek. Pomiar (pełna klatka: krok + render, okno 1200×800):

| Mrówki | ms / klatkę | ~FPS |
|-------:|------------:|-----:|
| 120    | 4.0         | 249  |
| 400    | 9.0         | 111  |
| 800    | 16.0        | 63   |

Siatka feromonów (parowanie + dyfuzja, wektorowo w numpy) to ~0.4 ms/klatkę i nie
jest wąskim gardłem. Pętla jest ograniczona do `fps` z konfiguracji.

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
- [x] Etap 4 — przeszkody i interaktywna mapa (mysz)
- [x] Etap 5 — panel sterowania na żywo (suwaki, przełączniki)
- [x] Etap 6 — statystyki i wykresy w czasie
- [ ] Etap 7 — życie kolonii (głód, narodziny, drapieżniki) — *pominięty na życzenie*
- [x] Etap 8 — wydajność, hardening, dokumentacja
- [ ] Etap 9 — eksploratorzy vs. szlak: optymalizacja (skracanie) tras
- [ ] Etap 10 — debug: powrót inną trasą niż dojście (weryfikacja błędu)

### Etap 9 — eksploratorzy vs. mrówki podążające szlakiem (optymalizacja tras)

**Problem (zaobserwowany):** gdy szlak gniazdo↔jedzenie już powstanie, „zastyga" —
mrówki w kółko chodzą tą samą (często krętą, nieoptymalną) trasą i nie skraca się
ona z czasem. W prawdziwej kolonii szlaki dążą do najkrótszej ścieżki.

**Dlaczego tak jest teraz:** wszystkie mrówki mają jednakowe parametry i mocno
trzymają się feromonu (`trail_rejoin_chance = 1.0`, jednolita `pheromone_weight`).
Po uformowaniu szlaku nikt nie szuka skrótów, więc brak dodatniego sprzężenia,
które przeniosłoby ruch na krótszą trasę.

**Plan:**
- **Role mrówek** (np. dataclass `AntProfile` lub typ Eksplorator/Robotnica),
  przydzielane przy tworzeniu wg `explorer_ratio` z konfiguracji (**domyślnie 10%**).
  - *Eksploratorzy* (mniejszość): wysoki `wander`, niska waga feromonu, ignorują
    `trail_rejoin` — aktywnie szukają skrótów i wariantów trasy.
  - *Robotnice* (większość): jak teraz — eksploatują szlak.
- **Suwak „% eksploratorów" w panelu sterowania** (`ControlPanel`) — regulacja na
  żywo (zakres 0–100%, start 10%); zmiana przelicza role w istniejącej kolonii.
- **Optymalizacja przez sprzężenie zwrotne:** krótsza trasa = szybszy obieg =
  częstszy depozyt → samoistne wzmacnianie skrótu; przy odpowiednim parowaniu
  dłuższy wariant zanika. Dostroić `evaporation`/depozyt tak, by nieużywane
  odcinki gasły i szlak mógł się „przepiąć".
- **Render:** odróżnić eksploratorów kolorem (opcjonalny przełącznik).
- **Pomiar:** dodać metrykę zbieżności do benchmarku — np. średni czas obiegu
  (round-trip) lub długość szlaku w czasie, by potwierdzić skracanie trasy.
- **Testy:** przydział ról wg proporcji; eksplorator błądzi bardziej (mniejszy
  wpływ feromonu na kierunek) niż robotnica.

### Etap 10 — debug: powrót inną trasą niż dojście (weryfikacja)

**Problem (zaobserwowany):** mrówka idąca do jedzenia po szlaku feromonowym czasem
**nie wraca tym samym szlakiem** — odbija na całkiem przeciwną stronę.

**Hipotezy do sprawdzenia (najpierw weryfikacja, czy to błąd):**
1. *Oczekiwana cecha ACO?* — dojście śledzi warstwę FOOD, powrót warstwę HOME; to
   dwa osobne ślady o różnej geometrii, więc trasa powrotna **może** się różnić.
   Trzeba ocenić, czy „druga strona" to naturalny wariant, czy patologia.
2. `ReturningState.on_enter` ustawia kurs **wprost na gniazdo**; jeśli szlak HOME
   przy jedzeniu jest słaby/rozwidlony, czujniki mogą złapać inną gałąź i poprowadzić
   mrówkę naokoło.
3. Limit skrętu (`ant_max_turn`) przy ~180° zawróceniu na jedzeniu może powodować
   „okrążanie" zamiast zawrotu.
4. Artefakt gradientu HOME w pobliżu jedzenia (pętla/stary depozyt) wskazujący zły
   kierunek.

**Plan diagnozy:**
- Tryb debug: śledzenie i rysowanie trasy **jednej** mrówki (dojście vs. powrót).
- Scenariusz kontrolny: jedno źródło jedzenia, brak przeszkód — sprawdzić, czy
  rozjazd jest systematyczny i jak częsty.
- Werdykt: jeśli błąd — rozważyć fix (np. start powrotu z uwzględnieniem kierunku,
  którym mrówka przyszła; spójniejszy gradient HOME), jeśli cecha — opisać i ew.
  zredukować parametrami.
