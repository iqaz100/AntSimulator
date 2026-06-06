# ===== KONFIGURACJA SYMULATORA MRÓWEK =====
# Możesz łatwo dostosować parametry symulatora zmieniając wartości poniżej

# ===== PODSTAWOWE USTAWIENIA =====
# Włącz/wyłącz różne funkcje symulatora
ENABLE_OBSTACLES = True           # System przeszkód
ENABLE_ADVANCED_NAVIGATION = True # Zaawansowana nawigacja
ENABLE_PHEROMONE_GRADIENT = True  # Gradient feromonów
ENABLE_ANT_MEMORY = True          # Pamięć mrówek
ENABLE_DYNAMIC_SPEED = True       # Dynamiczna prędkość
ENABLE_ANT_SPECIALIZATION = True  # Specjalizacja mrówek

# ===== PARAMETRY OKNA =====
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60

# ===== PARAMETRY PRZESZKÓD =====
OBSTACLE_COUNT = 8               # Liczba przeszkód na planszy
OBSTACLE_MIN_SIZE = 20           # Minimalny rozmiar przeszkody
OBSTACLE_MAX_SIZE = 60           # Maksymalny rozmiar przeszkody
OBSTACLE_COLOR = (100, 100, 100) # Kolor przeszkód (RGB)

# ===== PARAMETRY NAWIGACJI =====
NAVIGATION_RANGE = 80            # Zasięg wykrywania feromonów
MEMORY_SIZE = 10                 # Rozmiar pamięci mrówki
SPECIALIZATION_TYPES = ['scout', 'collector', 'guard']  # Dostępne typy specjalizacji

# ===== PARAMETRY FEROMONÓW =====
PHEROMONE_DECAY_RATE = 0.98      # Szybkość zanikania feromonów (0-1)
PHEROMONE_STRENGTH_MULTIPLIER = 1.5  # Mnożnik siły feromonów

# ===== PARAMETRY MRÓWEK =====
INITIAL_ANT_COUNT = 50           # Początkowa liczba mrówek
ANT_BASE_SPEED = 2               # Podstawowa prędkość mrówki
ANT_RADIUS = 3                   # Promień mrówki
MAX_FOOD_CAPACITY = 3            # Maksymalna pojemność na jedzenie

# ===== PARAMETRY JEDZENIA =====
FOOD_SPAWN_COUNT = 5             # Liczba porcji jedzenia do wygenerowania
FOOD_MIN_AMOUNT = 20             # Minimalna ilość jedzenia
FOOD_MAX_AMOUNT = 50             # Maksymalna ilość jedzenia
FOOD_MIN_DISTANCE = 15           # Minimalna odległość od przeszkód

# ===== PARAMETRY GNIAZDA =====
NEST_RADIUS = 30                 # Promień gniazda

# ===== KOLORY =====
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)

# ===== PARAMETRY SPECJALIZACJI =====
# Zwiadowcy
SCOUT_SPEED_MULTIPLIER = 1.5
SCOUT_PHEROMONE_RATE = 0.5
SCOUT_WANDER_DISTANCE = 30

# Zbieracze
COLLECTOR_SPEED_MULTIPLIER = 0.8
COLLECTOR_PHEROMONE_RATE = 0.4
COLLECTOR_FOOD_CAPACITY = 5

# Strażnicy
GUARD_SPEED_MULTIPLIER = 1.2
GUARD_RADIUS = 4
GUARD_PHEROMONE_SENSITIVITY = 0.7

# ===== PARAMETRY NAWIGACJI =====
STUCK_THRESHOLD = 30             # Liczba klatek przed uznaniem mrówki za zablokowaną
PATH_FINDING_ATTEMPTS = 16       # Liczba prób znalezienia ścieżki
AVOIDANCE_ANGLE_RANGE = 0.785    # Zakres kąta unikania (π/4)

# ===== PARAMETRY WĘDRÓWKI =====
WANDER_CHANGE_RATE = 0.1         # Szybkość zmiany kierunku wędrówki
WANDER_RADIUS = 10               # Promień losowego ruchu wokół celu
WANDER_DISTANCE = 20             # Odległość celu wędrówki

# ===== PARAMETRY FEROMONÓW =====
PHEROMONE_DROP_RATE = 0.3        # Częstotliwość zostawiania feromonów
PHEROMONE_SENSITIVITY = 0.5      # Wrażliwość na feromony
PHEROMONE_MIN_STRENGTH = 0.01    # Minimalna siła feromonu do wyświetlenia
PHEROMONE_VISIBILITY_THRESHOLD = 10  # Próg widoczności feromonu

# ===== PARAMETRY PAMIĘCI =====
MEMORY_VISIT_THRESHOLD = 20      # Próg odległości dla "niedawno odwiedzonego"
MEMORY_FOOD_CHECK_DISTANCE = 50  # Odległość sprawdzania znanych lokalizacji jedzenia

# ===== PARAMETRY KOLIZJI =====
COLLISION_DETECTION_RADIUS = 3   # Promień wykrywania kolizji mrówki
FOOD_COLLISION_RADIUS = 15       # Promień wykrywania kolizji jedzenia

# ===== PARAMETRY INTERFEJSU =====
FONT_SIZE_LARGE = 36             # Rozmiar dużego tekstu
FONT_SIZE_SMALL = 24             # Rozmiar małego tekstu
STATS_UPDATE_RATE = 1            # Częstotliwość aktualizacji statystyk

# ===== PARAMETRY STEROWANIA =====
ANTS_PER_SPACE_PRESS = 10        # Liczba mrówek dodawanych przez SPACJĘ
FOOD_PER_F_PRESS = 5             # Liczba porcji jedzenia dodawanych przez F
OBSTACLES_PER_O_PRESS = 1        # Liczba przeszkód dodawanych przez O 