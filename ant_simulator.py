import pygame
import random
import math
import numpy as np
from typing import List, Tuple, Optional
import colorsys

# Inicjalizacja PyGame
pygame.init()

# ===== KONFIGURACJA PARAMETRÓW =====
# Możesz włączać/wyłączać funkcje zmieniając te wartości na True/False

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
OBSTACLE_COLOR = (100, 100, 100) # Kolor przeszkód

# Parametry zaawansowanej nawigacji
NAVIGATION_RANGE = 80            # Zasięg wykrywania feromonów
MEMORY_SIZE = 10                 # Rozmiar pamięci mrówki
SPECIALIZATION_TYPES = ['scout', 'collector', 'guard']  # Typy specjalizacji

# Parametry feromonów
PHEROMONE_DECAY_RATE = 0.98      # Szybkość zanikania feromonów
PHEROMONE_STRENGTH_MULTIPLIER = 1.5  # Mnożnik siły feromonów

# Stałe
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60

# Kolory
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)

class Obstacle:
    """Klasa reprezentująca przeszkodę na planszy"""
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        
    def collides_with(self, x: float, y: float, radius: int = 0) -> bool:
        """Sprawdza czy punkt koliduje z przeszkodą"""
        if radius == 0:
            return self.rect.collidepoint(x, y)
        else:
            # Sprawdź czy okrąg koliduje z prostokątem
            closest_x = max(self.x, min(x, self.x + self.width))
            closest_y = max(self.y, min(y, self.y + self.height))
            distance = math.sqrt((x - closest_x)**2 + (y - closest_y)**2)
            return distance <= radius
            
    def draw(self, screen):
        """Rysuje przeszkodę"""
        pygame.draw.rect(screen, OBSTACLE_COLOR, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

class AntMemory:
    """Klasa reprezentująca pamięć mrówki"""
    def __init__(self, size: int):
        self.size = size
        self.positions = []  # Lista ostatnich pozycji
        self.food_locations = []  # Lista znalezionych lokalizacji jedzenia
        self.obstacle_locations = []  # Lista napotkanych przeszkód
        
    def add_position(self, x: float, y: float):
        """Dodaje pozycję do pamięci"""
        self.positions.append((x, y))
        if len(self.positions) > self.size:
            self.positions.pop(0)
            
    def add_food_location(self, x: float, y: float):
        """Dodaje lokalizację jedzenia do pamięci"""
        if (x, y) not in self.food_locations:
            self.food_locations.append((x, y))
            if len(self.food_locations) > self.size // 2:
                self.food_locations.pop(0)
                
    def add_obstacle_location(self, x: float, y: float):
        """Dodaje lokalizację przeszkody do pamięci"""
        if (x, y) not in self.obstacle_locations:
            self.obstacle_locations.append((x, y))
            if len(self.obstacle_locations) > self.size // 2:
                self.obstacle_locations.pop(0)
                
    def get_recent_positions(self) -> List[Tuple[float, float]]:
        """Zwraca ostatnie pozycje"""
        return self.positions.copy()
        
    def is_recently_visited(self, x: float, y: float, threshold: float = 20) -> bool:
        """Sprawdza czy pozycja była niedawno odwiedzona"""
        for pos_x, pos_y in self.positions:
            distance = math.sqrt((x - pos_x)**2 + (y - pos_y)**2)
            if distance < threshold:
                return True
        return False

class Pheromone:
    """Klasa reprezentująca feromon na planszy"""
    def __init__(self, x: int, y: int, strength: float, pheromone_type: str):
        self.x = x
        self.y = y
        self.strength = strength  # Siła feromonu (0-1)
        self.pheromone_type = pheromone_type  # 'food' lub 'home'
        self.decay_rate = PHEROMONE_DECAY_RATE  # Szybkość zanikania feromonu
        self.creation_time = pygame.time.get_ticks()  # Czas utworzenia
        
    def update(self):
        """Aktualizuje siłę feromonu (zanikanie)"""
        self.strength *= self.decay_rate
        
    def get_color(self) -> Tuple[int, int, int]:
        """Zwraca kolor feromonu na podstawie typu i siły"""
        # Upewnij się, że siła jest w zakresie 0-1
        strength = max(0, min(1, self.strength))
        
        if self.pheromone_type == 'food':
            # Zielony dla feromonów jedzenia
            intensity = int(255 * strength)
            return (0, intensity, 0)
        else:
            # Niebieski dla feromonów powrotu
            intensity = int(255 * strength)
            return (0, 0, intensity)
            
    def get_gradient_strength(self, distance: float) -> float:
        """Zwraca siłę feromonu z uwzględnieniem gradientu"""
        if not ENABLE_PHEROMONE_GRADIENT:
            return self.strength
            
        # Gradient maleje z odległością
        max_distance = NAVIGATION_RANGE
        if distance > max_distance:
            return 0
        return self.strength * (1 - distance / max_distance)

class Food:
    """Klasa reprezentująca jedzenie na planszy"""
    def __init__(self, x: int, y: int, amount: int):
        self.x = x
        self.y = y
        self.amount = amount  # Ilość jedzenia
        self.max_amount = amount
        
    def take_food(self, amount: int = 1) -> int:
        """Pobiera jedzenie i zwraca ile faktycznie pobrano"""
        if self.amount >= amount:
            self.amount -= amount
            return amount
        else:
            taken = self.amount
            self.amount = 0
            return taken
            
    def is_empty(self) -> bool:
        """Sprawdza czy jedzenie się skończyło"""
        return self.amount <= 0
        
    def get_color(self) -> Tuple[int, int, int]:
        """Zwraca kolor jedzenia na podstawie ilości"""
        ratio = self.amount / self.max_amount
        intensity = int(255 * ratio)
        return (intensity, intensity, 0)  # Żółty z intensywnością

class Nest:
    """Klasa reprezentująca gniazdo mrówek"""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.radius = 30
        self.food_stored = 0
        
    def store_food(self, amount: int):
        """Przechowuje jedzenie w gnieździe"""
        self.food_stored += amount
        
    def draw(self, screen):
        """Rysuje gniazdo"""
        pygame.draw.circle(screen, BROWN, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, BLACK, (self.x, self.y), self.radius, 2)
        
        # Wyświetl ilość przechowywanego jedzenia
        font = pygame.font.Font(None, 24)
        text = font.render(f"Jedzenie: {self.food_stored}", True, WHITE)
        screen.blit(text, (self.x - 50, self.y - 40))

class Ant:
    """Klasa reprezentująca mrówkę"""
    def __init__(self, x: int, y: int, nest: Nest):
        self.x = x
        self.y = y
        self.nest = nest
        self.radius = 3
        self.base_speed = 2
        self.speed = self.base_speed
        self.angle = random.uniform(0, 2 * math.pi)
        self.has_food = False
        self.food_amount = 0
        self.max_food_capacity = 3
        
        # Parametry wędrówki
        self.wander_angle = 0
        self.wander_change = 0.1
        self.wander_radius = 10
        self.wander_distance = 20
        
        # Parametry feromonów
        self.pheromone_drop_rate = 0.3
        self.pheromone_sensitivity = 0.5
        
        # Pamięć mrówki
        self.memory = AntMemory(MEMORY_SIZE)
        
        # Specjalizacja mrówki
        if ENABLE_ANT_SPECIALIZATION:
            self.specialization = random.choice(SPECIALIZATION_TYPES)
            self._apply_specialization()
        else:
            self.specialization = 'general'
            
        # Parametry zaawansowanej nawigacji
        self.stuck_time = 0
        self.last_position = (x, y)
        self.avoidance_angle = 0
        
    def _apply_specialization(self):
        """Stosuje specjalizację do mrówki"""
        if self.specialization == 'scout':
            self.speed = self.base_speed * 1.5
            self.pheromone_drop_rate = 0.5
            self.wander_distance = 30
        elif self.specialization == 'collector':
            self.max_food_capacity = 5
            self.pheromone_drop_rate = 0.4
            self.speed = self.base_speed * 0.8
        elif self.specialization == 'guard':
            self.speed = self.base_speed * 1.2
            self.radius = 4
            self.pheromone_sensitivity = 0.7
        
    def update(self, pheromones: List[Pheromone], foods: List[Food], obstacles: List[Obstacle] = None):
        """Aktualizuje pozycję i stan mrówki"""
        if obstacles is None:
            obstacles = []
            
        # Sprawdź czy mrówka nie jest zablokowana
        self._check_if_stuck()
        
        # Dynamiczna prędkość
        if ENABLE_DYNAMIC_SPEED:
            self._update_speed()
            
        if self.has_food:
            # Mrówka ma jedzenie - wraca do gniazda
            self._return_to_nest(obstacles)
        else:
            # Mrówka szuka jedzenia
            self._search_for_food(pheromones, foods, obstacles)
            
        # Sprawdź kolizje z przeszkodami
        if ENABLE_OBSTACLES:
            self._handle_obstacle_collision(obstacles)
            
        # Aktualizuj pozycję
        new_x = self.x + math.cos(self.angle) * self.speed
        new_y = self.y + math.sin(self.angle) * self.speed
        
        # Sprawdź czy nowa pozycja nie koliduje z przeszkodami
        if not ENABLE_OBSTACLES or not self._position_collides_with_obstacles(new_x, new_y, obstacles):
            self.x = new_x
            self.y = new_y
        else:
            # Jeśli koliduje, spróbuj znaleźć alternatywną ścieżkę
            self._find_alternative_path(obstacles)
            
        # Ograniczenia planszy
        self.x = max(0, min(WINDOW_WIDTH, self.x))
        self.y = max(0, min(WINDOW_HEIGHT, self.y))
        
        # Dodaj pozycję do pamięci
        self.memory.add_position(self.x, self.y)
        
        # Zapisz ostatnią pozycję
        self.last_position = (self.x, self.y)
        
    def _check_if_stuck(self):
        """Sprawdza czy mrówka nie jest zablokowana"""
        if not ENABLE_ADVANCED_NAVIGATION:
            return
            
        distance_moved = math.sqrt((self.x - self.last_position[0])**2 + 
                                 (self.y - self.last_position[1])**2)
        
        if distance_moved < 1:
            self.stuck_time += 1
            if self.stuck_time > 30:  # Zablokowana przez 30 klatek
                self.angle += random.uniform(-math.pi/2, math.pi/2)
                self.stuck_time = 0
        else:
            self.stuck_time = 0
            
    def _update_speed(self):
        """Aktualizuje prędkość mrówki"""
        if not ENABLE_DYNAMIC_SPEED:
            return
            
        # Prędkość zależy od specjalizacji i stanu
        base_speed = self.base_speed
        
        if self.has_food:
            base_speed *= 0.8  # Wolniej z jedzeniem
        elif self.specialization == 'scout':
            base_speed *= 1.2  # Szybciej gdy szuka
            
        self.speed = base_speed
        
    def _position_collides_with_obstacles(self, x: float, y: float, obstacles: List[Obstacle]) -> bool:
        """Sprawdza czy pozycja koliduje z przeszkodami"""
        for obstacle in obstacles:
            if obstacle.collides_with(x, y, self.radius):
                return True
        return False
        
    def _handle_obstacle_collision(self, obstacles: List[Obstacle]):
        """Obsługuje kolizje z przeszkodami"""
        if not ENABLE_OBSTACLES:
            return
            
        for obstacle in obstacles:
            if obstacle.collides_with(self.x, self.y, self.radius):
                # Dodaj lokalizację przeszkody do pamięci
                self.memory.add_obstacle_location(self.x, self.y)
                
                # Oblicz kąt unikania
                dx = self.x - (obstacle.x + obstacle.width/2)
                dy = self.y - (obstacle.y + obstacle.height/2)
                self.avoidance_angle = math.atan2(dy, dx)
                
                # Zmień kierunek ruchu
                self.angle = self.avoidance_angle + random.uniform(-math.pi/4, math.pi/4)
                break
                
    def _find_alternative_path(self, obstacles: List[Obstacle]):
        """Znajduje alternatywną ścieżkę omijając przeszkody"""
        if not ENABLE_ADVANCED_NAVIGATION:
            return
            
        # Spróbuj różne kąty
        for i in range(8):
            test_angle = self.angle + (i * math.pi/4)
            test_x = self.x + math.cos(test_angle) * self.speed
            test_y = self.y + math.sin(test_angle) * self.speed
            
            if not self._position_collides_with_obstacles(test_x, test_y, obstacles):
                self.angle = test_angle
                return
                
        # Jeśli nie znajdzie ścieżki, zmień kierunek losowo
        self.angle = random.uniform(0, 2 * math.pi)
        
    def _find_path_to_target(self, target_x: float, target_y: float, obstacles: List[Obstacle]) -> float:
        """Znajduje ścieżkę do celu omijając przeszkody"""
        if not ENABLE_ADVANCED_NAVIGATION:
            return math.atan2(target_y - self.y, target_x - self.x)
            
        # Sprawdź czy bezpośrednia ścieżka jest możliwa
        direct_angle = math.atan2(target_y - self.y, target_x - self.x)
        test_x = self.x + math.cos(direct_angle) * self.speed
        test_y = self.y + math.sin(direct_angle) * self.speed
        
        if not self._position_collides_with_obstacles(test_x, test_y, obstacles):
            return direct_angle
            
        # Znajdź alternatywną ścieżkę
        for i in range(16):
            test_angle = direct_angle + (i * math.pi/8)
            test_x = self.x + math.cos(test_angle) * self.speed
            test_y = self.y + math.sin(test_angle) * self.speed
            
            if not self._position_collides_with_obstacles(test_x, test_y, obstacles):
                return test_angle
                
        # Jeśli nie znajdzie ścieżki, użyj losowego kąta
        return random.uniform(0, 2 * math.pi)
        
    def _return_to_nest(self, obstacles: List[Obstacle] = None):
        """Logika powrotu do gniazda"""
        if obstacles is None:
            obstacles = []
            
        # Oblicz kierunek do gniazda
        dx = self.nest.x - self.x
        dy = self.nest.y - self.y
        distance_to_nest = math.sqrt(dx*dx + dy*dy)
        
        if distance_to_nest < 20:
            # Mrówka dotarła do gniazda
            self.nest.store_food(self.food_amount)
            self.food_amount = 0
            self.has_food = False
            # Zmień kierunek na losowy
            self.angle = random.uniform(0, 2 * math.pi)
        else:
            # Kieruj się do gniazda z małym odchyleniem
            target_angle = math.atan2(dy, dx)
            
            # Sprawdź czy ścieżka do gniazda nie jest zablokowana
            if ENABLE_ADVANCED_NAVIGATION and obstacles:
                test_x = self.x + math.cos(target_angle) * self.speed
                test_y = self.y + math.sin(target_angle) * self.speed
                
                if self._position_collides_with_obstacles(test_x, test_y, obstacles):
                    # Znajdź alternatywną ścieżkę do gniazda
                    target_angle = self._find_path_to_target(self.nest.x, self.nest.y, obstacles)
            
            angle_diff = target_angle - self.angle
            
            # Normalizuj różnicę kątów
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
                
            # Płynnie skręć w kierunku gniazda
            self.angle += angle_diff * 0.1
            
    def _search_for_food(self, pheromones: List[Pheromone], foods: List[Food], obstacles: List[Obstacle] = None):
        """Logika poszukiwania jedzenia"""
        if obstacles is None:
            obstacles = []
            
        # Sprawdź pamięć mrówki dla znanych lokalizacji jedzenia
        if ENABLE_ANT_MEMORY and self.memory.food_locations:
            for food_x, food_y in self.memory.food_locations:
                dx = food_x - self.x
                dy = food_y - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < 50:  # Sprawdź znane lokalizacje
                    target_angle = self._find_path_to_target(food_x, food_y, obstacles)
                    angle_diff = target_angle - self.angle
                    
                    # Normalizuj różnicę kątów
                    while angle_diff > math.pi:
                        angle_diff -= 2 * math.pi
                    while angle_diff < -math.pi:
                        angle_diff += 2 * math.pi
                        
                    self.angle += angle_diff * 0.3
                    return
        
        # Sprawdź czy jest jedzenie w pobliżu
        for food in foods:
            if not food.is_empty():
                dx = food.x - self.x
                dy = food.y - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < 15:
                    # Znaleziono jedzenie
                    taken = food.take_food(self.max_food_capacity)
                    if taken > 0:
                        self.food_amount = taken
                        self.has_food = True
                        # Dodaj lokalizację jedzenia do pamięci
                        self.memory.add_food_location(food.x, food.y)
                        return
        
        # Sprawdź feromony jedzenia w pobliżu z uwzględnieniem gradientu
        nearby_food_pheromones = []
        for pheromone in pheromones:
            if pheromone.pheromone_type == 'food' and pheromone.strength > 0.1:
                dx = pheromone.x - self.x
                dy = pheromone.y - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < NAVIGATION_RANGE:
                    # Użyj gradientu feromonów
                    strength = pheromone.get_gradient_strength(distance)
                    if strength > 0.05:
                        nearby_food_pheromones.append((pheromone, distance, strength))
        
        if nearby_food_pheromones:
            # Kieruj się w stronę najsilniejszego feromonu
            strongest_pheromone = max(nearby_food_pheromones, 
                                    key=lambda x: x[2] / (x[1] + 1))
            pheromone, distance, strength = strongest_pheromone
            
            dx = pheromone.x - self.x
            dy = pheromone.y - self.y
            target_angle = math.atan2(dy, dx)
            
            # Dodaj losowość do ruchu
            target_angle += random.uniform(-0.3, 0.3)
            
            # Sprawdź czy ścieżka do feromonu nie jest zablokowana
            if ENABLE_ADVANCED_NAVIGATION:
                test_x = self.x + math.cos(target_angle) * self.speed
                test_y = self.y + math.sin(target_angle) * self.speed
                
                if self._position_collides_with_obstacles(test_x, test_y, obstacles):
                    target_angle = self._find_path_to_target(pheromone.x, pheromone.y, obstacles)
            
            # Płynnie skręć w kierunku feromonu
            angle_diff = target_angle - self.angle
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
                
            self.angle += angle_diff * 0.2
        else:
            # Wędruj losowo z uwzględnieniem przeszkód
            self._wander(obstacles)
            
    def _wander(self, obstacles: List[Obstacle] = None):
        """Losowe wędrowanie mrówki z uwzględnieniem przeszkód"""
        if obstacles is None:
            obstacles = []
            
        # Aktualizuj kąt wędrówki
        self.wander_angle += random.uniform(-self.wander_change, self.wander_change)
        
        # Oblicz pozycję celu wędrówki
        wander_x = self.x + math.cos(self.wander_angle) * self.wander_distance
        wander_y = self.y + math.sin(self.wander_angle) * self.wander_distance
        
        # Dodaj losowy ruch wokół celu
        wander_x += random.uniform(-self.wander_radius, self.wander_radius)
        wander_y += random.uniform(-self.wander_radius, self.wander_radius)
        
        # Sprawdź czy cel wędrówki nie jest w przeszkodzie
        if ENABLE_OBSTACLES:
            for obstacle in obstacles:
                if obstacle.collides_with(wander_x, wander_y):
                    # Wybierz nowy cel wędrówki
                    self.wander_angle = random.uniform(0, 2 * math.pi)
                    wander_x = self.x + math.cos(self.wander_angle) * self.wander_distance
                    wander_y = self.y + math.sin(self.wander_angle) * self.wander_distance
                    break
        
        # Kieruj się do celu wędrówki
        dx = wander_x - self.x
        dy = wander_y - self.y
        target_angle = math.atan2(dy, dx)
        
        # Sprawdź czy ścieżka do celu nie jest zablokowana
        if ENABLE_ADVANCED_NAVIGATION:
            test_x = self.x + math.cos(target_angle) * self.speed
            test_y = self.y + math.sin(target_angle) * self.speed
            
            if self._position_collides_with_obstacles(test_x, test_y, obstacles):
                target_angle = self._find_path_to_target(wander_x, wander_y, obstacles)
        
        # Płynnie skręć
        angle_diff = target_angle - self.angle
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
            
        self.angle += angle_diff * 0.1
        
    def drop_pheromone(self, pheromones: List[Pheromone]):
        """Zostawia feromon na planszy"""
        if random.random() < self.pheromone_drop_rate:
            pheromone_type = 'food' if self.has_food else 'home'
            strength = (1.0 if self.has_food else 0.5) * PHEROMONE_STRENGTH_MULTIPLIER
            
            # Specjalizacja wpływa na siłę feromonów
            if ENABLE_ANT_SPECIALIZATION:
                if self.specialization == 'scout':
                    strength *= 1.5
                elif self.specialization == 'collector':
                    strength *= 1.2
                    
            pheromones.append(Pheromone(int(self.x), int(self.y), strength, pheromone_type))
            
    def draw(self, screen):
        """Rysuje mrówkę"""
        # Kolor zależy od stanu i specjalizacji
        if self.has_food:
            color = ORANGE
        elif ENABLE_ANT_SPECIALIZATION:
            if self.specialization == 'scout':
                color = (255, 0, 255)  # Magenta dla zwiadowców
            elif self.specialization == 'collector':
                color = (0, 255, 255)  # Cyan dla zbieraczy
            elif self.specialization == 'guard':
                color = (255, 255, 0)  # Żółty dla strażników
            else:
                color = RED
        else:
            color = RED
            
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        
        # Rysuj kierunek ruchu
        end_x = self.x + math.cos(self.angle) * 8
        end_y = self.y + math.sin(self.angle) * 8
        pygame.draw.line(screen, BLACK, (self.x, self.y), (end_x, end_y), 2)
        
        # Rysuj specjalizację (mały kwadrat)
        if ENABLE_ANT_SPECIALIZATION and self.specialization != 'general':
            spec_x = int(self.x) + 6
            spec_y = int(self.y) - 6
            pygame.draw.rect(screen, BLACK, (spec_x, spec_y, 3, 3))

class AntSimulator:
    """Główna klasa symulatora"""
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Symulator Mrówek")
        self.clock = pygame.time.Clock()
        
        # Inicjalizacja obiektów
        self.nest = Nest(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.ants = []
        self.foods = []
        self.pheromones = []
        self.obstacles = []
        
        # Stwórz przeszkody
        if ENABLE_OBSTACLES:
            for _ in range(OBSTACLE_COUNT):
                x = random.randint(100, WINDOW_WIDTH - 100)
                y = random.randint(100, WINDOW_HEIGHT - 100)
                w = random.randint(OBSTACLE_MIN_SIZE, OBSTACLE_MAX_SIZE)
                h = random.randint(OBSTACLE_MIN_SIZE, OBSTACLE_MAX_SIZE)
                self.obstacles.append(Obstacle(x, y, w, h))
            
        # Stwórz początkowe mrówki
        for _ in range(50):
            x = self.nest.x + random.uniform(-50, 50)
            y = self.nest.y + random.uniform(-50, 50)
            self.ants.append(Ant(int(x), int(y), self.nest))
            
        # Stwórz jedzenie
        self._spawn_food()
        
    def _spawn_food(self):
        """Tworzy nowe jedzenie na planszy"""
        for _ in range(5):
            attempts = 0
            while attempts < 50:  # Maksymalnie 50 prób
                x = random.randint(100, WINDOW_WIDTH - 100)
                y = random.randint(100, WINDOW_HEIGHT - 100)
                
                # Sprawdź czy pozycja nie koliduje z przeszkodami
                valid_position = True
                if ENABLE_OBSTACLES:
                    for obstacle in self.obstacles:
                        if obstacle.collides_with(x, y, 15):  # Promień 15 dla jedzenia
                            valid_position = False
                            break
                            
                if valid_position:
                    amount = random.randint(20, 50)
                    self.foods.append(Food(x, y, amount))
                    break
                    
                attempts += 1
            
    def update(self):
        """Aktualizuje stan symulatora"""
        # Aktualizuj mrówki
        for ant in self.ants:
            ant.update(self.pheromones, self.foods, self.obstacles)
            ant.drop_pheromone(self.pheromones)
            
        # Aktualizuj feromony
        for pheromone in self.pheromones[:]:
            pheromone.update()
            if pheromone.strength < 0.01:
                self.pheromones.remove(pheromone)
                
        # Usuń puste jedzenie i stwórz nowe
        self.foods = [food for food in self.foods if not food.is_empty()]
        if len(self.foods) < 3:
            self._spawn_food()
            
    def draw(self):
        """Rysuje wszystkie obiekty"""
        self.screen.fill(WHITE)
        
        # Rysuj przeszkody
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        # Rysuj feromony
        for pheromone in self.pheromones:
            try:
                color = pheromone.get_color()
                alpha = int(255 * pheromone.strength)
                if alpha > 10:  # Rysuj tylko widoczne feromony
                    pygame.draw.circle(self.screen, color, (pheromone.x, pheromone.y), 2)
            except (ValueError, TypeError) as e:
                # Jeśli wystąpi błąd z kolorem, pomiń ten feromon
                continue
                
        # Rysuj jedzenie
        for food in self.foods:
            color = food.get_color()
            pygame.draw.circle(self.screen, color, (food.x, food.y), 10)
            pygame.draw.circle(self.screen, BLACK, (food.x, food.y), 10, 2)
            
        # Rysuj gniazdo
        self.nest.draw(self.screen)
        
        # Rysuj mrówki
        for ant in self.ants:
            ant.draw(self.screen)
            
        # Wyświetl statystyki
        font = pygame.font.Font(None, 36)
        stats_text = f"Mrówki: {len(self.ants)} | Jedzenie: {len(self.foods)} | Feromony: {len(self.pheromones)}"
        if ENABLE_OBSTACLES:
            stats_text += f" | Przeszkody: {len(self.obstacles)}"
        text_surface = font.render(stats_text, True, BLACK)
        self.screen.blit(text_surface, (10, 10))
        
        # Wyświetl informacje o funkcjach
        font_small = pygame.font.Font(None, 24)
        y_offset = 40
        if ENABLE_OBSTACLES:
            text = font_small.render("Przeszkody: WŁĄCZONE", True, GREEN)
            self.screen.blit(text, (10, y_offset))
            y_offset += 25
        if ENABLE_ADVANCED_NAVIGATION:
            text = font_small.render("Zaawansowana nawigacja: WŁĄCZONA", True, GREEN)
            self.screen.blit(text, (10, y_offset))
            y_offset += 25
        if ENABLE_ANT_SPECIALIZATION:
            text = font_small.render("Specjalizacja mrówek: WŁĄCZONA", True, GREEN)
            self.screen.blit(text, (10, y_offset))
            y_offset += 25
        if ENABLE_ANT_MEMORY:
            text = font_small.render("Pamięć mrówek: WŁĄCZONA", True, GREEN)
            self.screen.blit(text, (10, y_offset))
        
        pygame.display.flip()
        
    def run(self):
        """Główna pętla gry"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        # Dodaj nowe mrówki
                        for _ in range(10):
                            x = self.nest.x + random.uniform(-50, 50)
                            y = self.nest.y + random.uniform(-50, 50)
                            self.ants.append(Ant(int(x), int(y), self.nest))
                    elif event.key == pygame.K_f:
                        # Dodaj nowe jedzenie
                        self._spawn_food()
                    elif event.key == pygame.K_o:
                        # Dodaj nową przeszkodę
                        if ENABLE_OBSTACLES:
                            x = random.randint(100, WINDOW_WIDTH - 100)
                            y = random.randint(100, WINDOW_HEIGHT - 100)
                            w = random.randint(OBSTACLE_MIN_SIZE, OBSTACLE_MAX_SIZE)
                            h = random.randint(OBSTACLE_MIN_SIZE, OBSTACLE_MAX_SIZE)
                            self.obstacles.append(Obstacle(x, y, w, h))
                    elif event.key == pygame.K_r:
                        # Resetuj przeszkody
                        if ENABLE_OBSTACLES:
                            self.obstacles.clear()
                            for _ in range(OBSTACLE_COUNT):
                                x = random.randint(100, WINDOW_WIDTH - 100)
                                y = random.randint(100, WINDOW_HEIGHT - 100)
                                w = random.randint(OBSTACLE_MIN_SIZE, OBSTACLE_MAX_SIZE)
                                h = random.randint(OBSTACLE_MIN_SIZE, OBSTACLE_MAX_SIZE)
                                self.obstacles.append(Obstacle(x, y, w, h))
                        
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    simulator = AntSimulator()
    simulator.run() 