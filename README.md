# Symulator Mrówek - Rozszerzona Wersja

Zaawansowany symulator mrówek napisany w Pythonie z użyciem PyGame, który demonstruje realistyczne zachowanie mrówek w poszukiwaniu jedzenia, komunikacji za pomocą feromonów oraz nawigacji w środowisku z przeszkodami.

## 🆕 Nowe Funkcjonalności

### 🚧 System Przeszkód
- **Dynamiczne przeszkody**: Mrówki omijają przeszkody używając zaawansowanych algorytmów nawigacji
- **Kolizje**: System wykrywania kolizji z przeszkodami
- **Alternatywne ścieżki**: Mrówki znajdują alternatywne drogi gdy główna ścieżka jest zablokowana

### 🧠 Zaawansowana Nawigacja
- **Pamięć mrówek**: Mrówki pamiętają lokalizacje jedzenia i przeszkód
- **Gradient feromonów**: Siła feromonów maleje z odległością
- **Wykrywanie zablokowania**: Mrówki wykrywają gdy są zablokowane i zmieniają kierunek
- **Dynamiczna prędkość**: Prędkość mrówki zależy od jej stanu i specjalizacji

### 👥 Specjalizacja Mrówek
- **Zwiadowcy** (Magenta): Szybkie mrówki z większym zasięgiem wędrówki
- **Zbieracze** (Cyan): Mrówki z większą pojemnością na jedzenie
- **Strażnicy** (Żółty): Mrówki z lepszym wykrywaniem feromonów

## ⚙️ Konfiguracja Parametrów

Wszystkie funkcje można włączać/wyłączać edytując parametry na początku pliku `ant_simulator.py`:

```python
# Podstawowe ustawienia
ENABLE_OBSTACLES = True           # Włącz/wyłącz przeszkody
ENABLE_ADVANCED_NAVIGATION = True # Włącz/wyłącz zaawansowaną nawigację
ENABLE_PHEROMONE_GRADIENT = True  # Włącz/wyłącz gradient feromonów
ENABLE_ANT_MEMORY = True          # Włącz/wyłącz pamięć mrówek
ENABLE_DYNAMIC_SPEED = True       # Włącz/wyłącz dynamiczną prędkość
ENABLE_ANT_SPECIALIZATION = True  # Włącz/wyłącz specjalizację mrówek

# Parametry przeszkód
OBSTACLE_COUNT = 8               # Liczba przeszkód
OBSTACLE_MIN_SIZE = 20           # Minimalny rozmiar przeszkody
OBSTACLE_MAX_SIZE = 60           # Maksymalny rozmiar przeszkody

# Parametry zaawansowanej nawigacji
NAVIGATION_RANGE = 80            # Zasięg wykrywania feromonów
MEMORY_SIZE = 10                 # Rozmiar pamięci mrówki
```

## 🎮 Sterowanie

- **ESC** - Wyjście z symulatora
- **SPACJA** - Dodaj 10 nowych mrówek
- **F** - Dodaj nowe jedzenie na planszy
- **O** - Dodaj nową przeszkodę (jeśli przeszkody są włączone)
- **R** - Resetuj przeszkody (jeśli przeszkody są włączone)

## 🔬 Jak Działa Zaawansowany System

### System Przeszkód
1. **Wykrywanie kolizji**: Mrówki sprawdzają czy ich ścieżka nie jest zablokowana
2. **Znajdowanie alternatywnych ścieżek**: Algorytm testuje różne kąty ruchu
3. **Pamięć przeszkód**: Mrówki zapamiętują lokalizacje przeszkód
4. **Unikanie**: Mrówki omijają znane przeszkody

### Zaawansowana Nawigacja
1. **Pamięć lokalizacji**: Mrówki pamiętają gdzie znajdowały jedzenie
2. **Gradient feromonów**: Siła feromonów maleje z odległością
3. **Wykrywanie zablokowania**: Mrówki wykrywają gdy nie mogą się ruszyć
4. **Dynamiczne ścieżki**: Mrówki znajdują najlepsze ścieżki do celów

### Specjalizacja Mrówek
- **Zwiadowcy**: Szybkie, zostawiają silniejsze feromony, większy zasięg
- **Zbieracze**: Wolniejsze, większa pojemność na jedzenie
- **Strażnicy**: Lepsze wykrywanie feromonów, średnia prędkość

## 🎨 Wizualizacja

- **Czerwone mrówki**: Szukają jedzenia (podstawowe)
- **Pomarańczowe mrówki**: Niosą jedzenie do gniazda
- **Magenta mrówki**: Zwiadowcy
- **Cyan mrówki**: Zbieracze  
- **Żółte mrówki**: Strażnicy
- **Żółte koła**: Jedzenie (intensywność = ilość)
- **Brązowe koło**: Gniazdo mrówek
- **Szare prostokąty**: Przeszkody
- **Zielone/niebieskie punkty**: Feromony (z gradientem)

## 📊 Statystyki

Symulator wyświetla:
- Liczbę mrówek, jedzenia, feromonów
- Liczbę przeszkód (jeśli włączone)
- Status włączonych funkcji

## 🚀 Instalacja i Uruchomienie

1. Zainstaluj wymagane biblioteki:
```bash
pip install -r requirements.txt
```

2. Uruchom symulator:
```bash
python ant_simulator.py
```

## 📁 Struktura Projektu

- `ant_simulator.py` - Główny plik symulatora
- `config.py` - Plik konfiguracyjny z parametrami
- `example_configs.py` - Gotowe konfiguracje do testowania
- `requirements.txt` - Wymagane biblioteki
- `README.md` - Dokumentacja

## 🔧 Dostosowywanie

### Szybkie Konfiguracje

Symulator zawiera gotowe konfiguracje w pliku `example_configs.py`:

```python
from example_configs import load_config

# Załaduj gotową konfigurację
config = load_config('experimental')  # Eksperymentalna
config = load_config('maze')          # Labirynt
config = load_config('large')         # Duża kolonia
config = load_config('slow')          # Wolny symulator
```

### Dostępne Konfiguracje:
- **basic**: Podstawowy symulator (bez zaawansowanych opcji)
- **obstacles**: Z przeszkodami
- **advanced**: Zaawansowana nawigacja
- **specialization**: Ze specjalizacją mrówek
- **experimental**: Ekstremalne ustawienia
- **slow**: Wolny symulator
- **fast**: Szybki symulator
- **large**: Duża kolonia
- **small**: Mała kolonia
- **maze**: Labirynt

### Ręczne Dostosowywanie

Możesz eksperymentować z różnymi ustawieniami w `config.py`:

- **Wyłącz przeszkody**: `ENABLE_OBSTACLES = False`
- **Wyłącz specjalizację**: `ENABLE_ANT_SPECIALIZATION = False`
- **Zwiększ liczbę mrówek**: `INITIAL_ANT_COUNT = 100`
- **Zmień parametry feromonów**: `PHEROMONE_DECAY_RATE = 0.95`
- **Dostosuj prędkość**: `ANT_BASE_SPEED = 3`

## 🧪 Eksperymenty

Spróbuj różnych kombinacji ustawień:
- **Tylko podstawowe funkcje**: Wyłącz wszystkie zaawansowane opcje
- **Tylko przeszkody**: Włącz tylko `ENABLE_OBSTACLES`
- **Tylko specjalizacja**: Włącz tylko `ENABLE_ANT_SPECIALIZATION`
- **Pełna funkcjonalność**: Włącz wszystkie opcje

## 🎯 Technologie

- **Python 3.7+**
- **PyGame** - biblioteka do tworzenia gier
- **NumPy** - biblioteka do obliczeń matematycznych

## 🔬 Inspiracja

Symulator jest inspirowany rzeczywistym zachowaniem mrówek i algorytmami mrówkowymi (Ant Colony Optimization). Dodane funkcje demonstrują zaawansowane koncepcje sztucznej inteligencji i robotyki swarmowej. 