# ===== PRZYKŁADY KONFIGURACJI SYMULATORA MRÓWEK =====
# Możesz skopiować te konfiguracje do config.py aby przetestować różne scenariusze

# ===== KONFIGURACJA 1: PODSTAWOWY SYMULATOR =====
# Tylko podstawowe funkcje - bez przeszkód i zaawansowanych opcji
BASIC_CONFIG = {
    'ENABLE_OBSTACLES': False,
    'ENABLE_ADVANCED_NAVIGATION': False,
    'ENABLE_PHEROMONE_GRADIENT': False,
    'ENABLE_ANT_MEMORY': False,
    'ENABLE_DYNAMIC_SPEED': False,
    'ENABLE_ANT_SPECIALIZATION': False,
    'INITIAL_ANT_COUNT': 30,
    'FOOD_SPAWN_COUNT': 3,
    'PHEROMONE_DECAY_RATE': 0.99,
}

# ===== KONFIGURACJA 2: SYMULATOR Z PRZESZKODAMI =====
# Dodaje przeszkody ale bez zaawansowanej nawigacji
OBSTACLES_CONFIG = {
    'ENABLE_OBSTACLES': True,
    'ENABLE_ADVANCED_NAVIGATION': False,
    'ENABLE_PHEROMONE_GRADIENT': False,
    'ENABLE_ANT_MEMORY': False,
    'ENABLE_DYNAMIC_SPEED': False,
    'ENABLE_ANT_SPECIALIZATION': False,
    'OBSTACLE_COUNT': 5,
    'OBSTACLE_MIN_SIZE': 30,
    'OBSTACLE_MAX_SIZE': 80,
    'INITIAL_ANT_COUNT': 40,
}

# ===== KONFIGURACJA 3: ZAAWANSOWANA NAWIGACJA =====
# Włącza zaawansowaną nawigację i pamięć
ADVANCED_NAVIGATION_CONFIG = {
    'ENABLE_OBSTACLES': True,
    'ENABLE_ADVANCED_NAVIGATION': True,
    'ENABLE_PHEROMONE_GRADIENT': True,
    'ENABLE_ANT_MEMORY': True,
    'ENABLE_DYNAMIC_SPEED': True,
    'ENABLE_ANT_SPECIALIZATION': False,
    'NAVIGATION_RANGE': 100,
    'MEMORY_SIZE': 15,
    'PHEROMONE_DECAY_RATE': 0.97,
    'INITIAL_ANT_COUNT': 50,
}

# ===== KONFIGURACJA 4: SPECJALIZACJA MRÓWEK =====
# Włącza specjalizację mrówek
SPECIALIZATION_CONFIG = {
    'ENABLE_OBSTACLES': True,
    'ENABLE_ADVANCED_NAVIGATION': True,
    'ENABLE_PHEROMONE_GRADIENT': True,
    'ENABLE_ANT_MEMORY': True,
    'ENABLE_DYNAMIC_SPEED': True,
    'ENABLE_ANT_SPECIALIZATION': True,
    'INITIAL_ANT_COUNT': 60,
    'SCOUT_SPEED_MULTIPLIER': 2.0,
    'COLLECTOR_FOOD_CAPACITY': 8,
    'GUARD_PHEROMONE_SENSITIVITY': 0.9,
}

# ===== KONFIGURACJA 5: EKSPERYMENTALNA =====
# Ekstremalne ustawienia do testowania
EXPERIMENTAL_CONFIG = {
    'ENABLE_OBSTACLES': True,
    'ENABLE_ADVANCED_NAVIGATION': True,
    'ENABLE_PHEROMONE_GRADIENT': True,
    'ENABLE_ANT_MEMORY': True,
    'ENABLE_DYNAMIC_SPEED': True,
    'ENABLE_ANT_SPECIALIZATION': True,
    'INITIAL_ANT_COUNT': 100,
    'OBSTACLE_COUNT': 15,
    'FOOD_SPAWN_COUNT': 8,
    'PHEROMONE_DECAY_RATE': 0.95,
    'PHEROMONE_STRENGTH_MULTIPLIER': 2.0,
    'NAVIGATION_RANGE': 120,
    'MEMORY_SIZE': 20,
    'SCOUT_SPEED_MULTIPLIER': 2.5,
    'COLLECTOR_FOOD_CAPACITY': 10,
    'GUARD_RADIUS': 5,
}

# ===== KONFIGURACJA 6: WOLNY SYMULATOR =====
# Wolniejsze mrówki, dłużej trwające feromony
SLOW_CONFIG = {
    'ENABLE_OBSTACLES': True,
    'ENABLE_ADVANCED_NAVIGATION': True,
    'ENABLE_PHEROMONE_GRADIENT': True,
    'ENABLE_ANT_MEMORY': True,
    'ENABLE_DYNAMIC_SPEED': True,
    'ENABLE_ANT_SPECIALIZATION': True,
    'ANT_BASE_SPEED': 1,
    'PHEROMONE_DECAY_RATE': 0.995,
    'INITIAL_ANT_COUNT': 30,
    'FPS': 30,
    'SCOUT_SPEED_MULTIPLIER': 1.2,
    'COLLECTOR_SPEED_MULTIPLIER': 0.6,
    'GUARD_SPEED_MULTIPLIER': 0.8,
}

# ===== KONFIGURACJA 7: SZYBKI SYMULATOR =====
# Szybkie mrówki, szybko zanikające feromony
FAST_CONFIG = {
    'ENABLE_OBSTACLES': True,
    'ENABLE_ADVANCED_NAVIGATION': True,
    'ENABLE_PHEROMONE_GRADIENT': True,
    'ENABLE_ANT_MEMORY': True,
    'ENABLE_DYNAMIC_SPEED': True,
    'ENABLE_ANT_SPECIALIZATION': True,
    'ANT_BASE_SPEED': 4,
    'PHEROMONE_DECAY_RATE': 0.95,
    'INITIAL_ANT_COUNT': 80,
    'FPS': 120,
    'SCOUT_SPEED_MULTIPLIER': 2.0,
    'COLLECTOR_SPEED_MULTIPLIER': 1.0,
    'GUARD_SPEED_MULTIPLIER': 1.5,
}

# ===== KONFIGURACJA 8: DUŻA KOLONIA =====
# Duża liczba mrówek, dużo jedzenia
LARGE_COLONY_CONFIG = {
    'ENABLE_OBSTACLES': True,
    'ENABLE_ADVANCED_NAVIGATION': True,
    'ENABLE_PHEROMONE_GRADIENT': True,
    'ENABLE_ANT_MEMORY': True,
    'ENABLE_DYNAMIC_SPEED': True,
    'ENABLE_ANT_SPECIALIZATION': True,
    'INITIAL_ANT_COUNT': 150,
    'FOOD_SPAWN_COUNT': 12,
    'OBSTACLE_COUNT': 10,
    'WINDOW_WIDTH': 1600,
    'WINDOW_HEIGHT': 1000,
    'NAVIGATION_RANGE': 100,
    'MEMORY_SIZE': 15,
}

# ===== KONFIGURACJA 9: MAŁA KOLONIA =====
# Mała liczba mrówek, skupienie na szczegółach
SMALL_COLONY_CONFIG = {
    'ENABLE_OBSTACLES': True,
    'ENABLE_ADVANCED_NAVIGATION': True,
    'ENABLE_PHEROMONE_GRADIENT': True,
    'ENABLE_ANT_MEMORY': True,
    'ENABLE_DYNAMIC_SPEED': True,
    'ENABLE_ANT_SPECIALIZATION': True,
    'INITIAL_ANT_COUNT': 15,
    'FOOD_SPAWN_COUNT': 3,
    'OBSTACLE_COUNT': 3,
    'ANT_RADIUS': 5,
    'NAVIGATION_RANGE': 60,
    'MEMORY_SIZE': 8,
    'PHEROMONE_DECAY_RATE': 0.99,
}

# ===== KONFIGURACJA 10: LABIRYNT =====
# Wiele przeszkód tworzących labirynt
MAZE_CONFIG = {
    'ENABLE_OBSTACLES': True,
    'ENABLE_ADVANCED_NAVIGATION': True,
    'ENABLE_PHEROMONE_GRADIENT': True,
    'ENABLE_ANT_MEMORY': True,
    'ENABLE_DYNAMIC_SPEED': True,
    'ENABLE_ANT_SPECIALIZATION': True,
    'OBSTACLE_COUNT': 25,
    'OBSTACLE_MIN_SIZE': 40,
    'OBSTACLE_MAX_SIZE': 100,
    'INITIAL_ANT_COUNT': 40,
    'NAVIGATION_RANGE': 120,
    'MEMORY_SIZE': 20,
    'PATH_FINDING_ATTEMPTS': 32,
    'STUCK_THRESHOLD': 20,
}

# ===== FUNKCJA DO ŁADOWANIA KONFIGURACJI =====
def load_config(config_name):
    """
    Ładuje konfigurację na podstawie nazwy
    Dostępne konfiguracje:
    - 'basic': Podstawowy symulator
    - 'obstacles': Z przeszkodami
    - 'advanced': Zaawansowana nawigacja
    - 'specialization': Ze specjalizacją
    - 'experimental': Eksperymentalna
    - 'slow': Wolny symulator
    - 'fast': Szybki symulator
    - 'large': Duża kolonia
    - 'small': Mała kolonia
    - 'maze': Labirynt
    """
    configs = {
        'basic': BASIC_CONFIG,
        'obstacles': OBSTACLES_CONFIG,
        'advanced': ADVANCED_NAVIGATION_CONFIG,
        'specialization': SPECIALIZATION_CONFIG,
        'experimental': EXPERIMENTAL_CONFIG,
        'slow': SLOW_CONFIG,
        'fast': FAST_CONFIG,
        'large': LARGE_COLONY_CONFIG,
        'small': SMALL_COLONY_CONFIG,
        'maze': MAZE_CONFIG,
    }
    
    if config_name in configs:
        return configs[config_name]
    else:
        print(f"Nieznana konfiguracja: {config_name}")
        print("Dostępne konfiguracje:", list(configs.keys()))
        return BASIC_CONFIG

# ===== PRZYKŁAD UŻYCIA =====
if __name__ == "__main__":
    # Przykład ładowania konfiguracji
    config = load_config('experimental')
    print("Załadowana konfiguracja:", config)
    
    # Możesz skopiować te ustawienia do config.py
    print("\nAby użyć tej konfiguracji, skopiuj następujące linie do config.py:")
    for key, value in config.items():
        print(f"{key} = {value}") 