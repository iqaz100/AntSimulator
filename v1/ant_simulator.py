import pygame
import random
import math
from typing import List, Tuple

# Inicjalizacja PyGame
pygame.init()

# ===== KONFIGURACJA PARAMETRÓW =====
ENABLE_OBSTACLES = True
ENABLE_ADVANCED_NAVIGATION = True
ENABLE_PHEROMONE_GRADIENT = True
ENABLE_ANT_MEMORY = True
ENABLE_DYNAMIC_SPEED = True
ENABLE_ANT_SPECIALIZATION = True

# Parametry przeszkód
OBSTACLE_COUNT = 0
OBSTACLE_MIN_SIZE = 20
OBSTACLE_MAX_SIZE = 60
OBSTACLE_COLOR = (100, 100, 100)

# Parametry nawigacji
NAVIGATION_RANGE = 80
MEMORY_SIZE = 10
SPECIALIZATION_TYPES = ['scout', 'collector', 'guard']

# Parametry feromonów
PHEROMONE_DECAY_RATE = 0.995
PHEROMONE_STRENGTH_MULTIPLIER = 1.5

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
        self.positions = []
        self.food_locations = []
        
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
                
    def get_recent_positions(self) -> List[Tuple[float, float]]:
        """Zwraca ostatnie pozycje"""
        return self.positions.copy()

class Pheromone:
    """Klasa reprezentująca feromon na planszy"""
    def __init__(self, x: int, y: int, strength: float, pheromone_type: str):
        self.x = x
        self.y = y
        self.strength = strength
        self.pheromone_type = pheromone_type
        self.decay_rate = PHEROMONE_DECAY_RATE
        self.creation_time = pygame.time.get_ticks()
        self.decay_delay = 1200  # 20 sekund * 60 FPS
        
    def update(self):
        """Aktualizuje siłę feromonu (zanikanie po opóźnieniu)"""
        current_time = pygame.time.get_ticks()
        if current_time - self.creation_time > self.decay_delay:
            self.strength *= self.decay_rate
        
    def get_color(self) -> Tuple[int, int, int]:
        """Zwraca kolor feromonu na podstawie typu i siły"""
        strength = max(0, min(1, self.strength))
        intensity = int(255 * strength)
        
        if self.pheromone_type == 'food':
            return (0, intensity, 0)  # Zielony
        else:
            return (0, 0, intensity)  # Niebieski
            
    def get_gradient_strength(self, distance: float) -> float:
        """Zwraca siłę feromonu z uwzględnieniem gradientu"""
        if not ENABLE_PHEROMONE_GRADIENT:
            return self.strength
            
        max_distance = NAVIGATION_RANGE
        if distance > max_distance:
            return 0
        return self.strength * (1 - distance / max_distance)

class Food:
    """Klasa reprezentująca jedzenie na planszy"""
    def __init__(self, x: int, y: int, amount: int):
        self.x = x
        self.y = y
        self.amount = amount
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
        return (intensity, intensity, 0)

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
        self.base_speed = 1
        self.speed = self.base_speed
        self.angle = random.uniform(0, 2 * math.pi)
        self.has_food = False
        self.food_amount = 0
        self.max_food_capacity = 1
        
        # Parametry wędrówki
        self.wander_angle = 0
        self.wander_change = 0.1
        self.wander_radius = 10
        self.wander_distance = 20
        
        # Parametry feromonów
        self.pheromone_drop_rate = 0.3
        
        # Pamięć mrówki
        self.memory = AntMemory(MEMORY_SIZE)
        
        # Specjalizacja mrówki
        if ENABLE_ANT_SPECIALIZATION:
            self.specialization = random.choice(SPECIALIZATION_TYPES)
            self._apply_specialization()
        else:
            self.specialization = 'general'
            
        # Parametry nawigacji
        self.stuck_time = 0
        self.last_position = (x, y)
        
        # Stan po znalezieniu jedzenia
        self.waiting_after_food = False
        self.wait_counter = 0
        self.WAIT_FRAMES = FPS
        
        # Zapobieganie stagnacji
        self.last_positions = []
        self.STAGNATION_LIMIT = 40
        self.STAGNATION_RADIUS = 5
        
        # Ochrona przed ponownym podniesieniem jedzenia
        self.just_picked_food = False
        self.just_picked_counter = 0
        self.JUST_PICKED_FRAMES = 10
        
        # Ścieżka powrotu
        self.return_path = []
        self.return_path_index = None
        
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
        
    def _handle_edge_repulsion(self):
        """Obsługuje odpychanie od krawędzi planszy"""
        margin = 2
        repel_strength = 0.2
        
        if self.x < margin:
            self.angle += repel_strength * random.uniform(0.8, 1.2)
        elif self.x > WINDOW_WIDTH - margin:
            self.angle -= repel_strength * random.uniform(0.8, 1.2)
        if self.y < margin:
            self.angle += repel_strength * random.uniform(0.8, 1.2)
        elif self.y > WINDOW_HEIGHT - margin:
            self.angle -= repel_strength * random.uniform(0.8, 1.2)

    def _check_stagnation(self):
        """Sprawdza czy mrówka nie kręci się w kółko"""
        self.last_positions.append((self.x, self.y))
        if len(self.last_positions) > self.STAGNATION_LIMIT:
            self.last_positions.pop(0)
        if len(self.last_positions) == self.STAGNATION_LIMIT:
            d = math.sqrt((self.x - self.last_positions[0][0])**2 + 
                         (self.y - self.last_positions[0][1])**2)
            if d < self.STAGNATION_RADIUS:
                self.angle += random.uniform(math.pi/2, 3*math.pi/2)
                self.last_positions = []

    def _handle_food_pickup(self):
        """Obsługuje podniesienie jedzenia"""
        if self.wait_counter >= self.WAIT_FRAMES:
            self.waiting_after_food = False
            self.wait_counter = 0
            self.has_food = True
            
            # Ustaw kąt w stronę gniazda
            dx = self.nest.x - self.x
            dy = self.nest.y - self.y
            self.angle = math.atan2(dy, dx)
            
            # Odepchnij mrówkę od jedzenia
            # dist = 8
            # norm = math.sqrt(dx*dx + dy*dy)
            # if norm > 0:
            #     self.x += (dx / norm) * dist
            #     self.y += (dy / norm) * dist
            
            # # Ustaw ochronę przed ponownym podniesieniem
            # self.just_picked_food = True
            # self.just_picked_counter = 0
            
            # Zapamiętaj ścieżkę powrotu
            self.return_path = list(self.memory.get_recent_positions())[::-1]
            self.return_path_index = 0
            return True
        return False

    def _update_just_picked_counter(self):
        """Aktualizuje licznik ochrony przed ponownym podniesieniem jedzenia"""
        if self.just_picked_food:
            self.just_picked_counter += 1
            if self.just_picked_counter >= self.JUST_PICKED_FRAMES:
                self.just_picked_food = False

    def _return_via_path(self, obstacles: List[Obstacle]) -> bool:
        """Wraca do gniazda po zapamiętanej ścieżce"""
        if (self.return_path and self.return_path_index is not None and 
            self.return_path_index < len(self.return_path)):
            target = self.return_path[self.return_path_index]
            dx = target[0] - self.x
            dy = target[1] - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < 3:
                self.return_path_index += 1
            else:
                self.angle = math.atan2(dy, dx)
            return True
        return False

    def _normalize_angle_diff(self, target_angle: float) -> float:
        """Normalizuje różnicę kątów do zakresu [-π, π]"""
        angle_diff = target_angle - self.angle
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        return angle_diff

    def update(self, pheromones: List[Pheromone], foods: List[Food], obstacles: List[Obstacle] = None):
        """Aktualizuje pozycję i stan mrówki"""
        if obstacles is None:
            obstacles = []

        # Obsługa krawędzi i stagnacji
        self._handle_edge_repulsion()
        self._check_stagnation()

        # Oczekiwanie po znalezieniu jedzenia
        if self.waiting_after_food:
            self.wait_counter += 1
            if self._handle_food_pickup():
                return

        # Aktualizacja liczników
        # self._update_just_picked_counter()

        # Sprawdzenie zablokowania i prędkości
        self._check_if_stuck()
        if ENABLE_DYNAMIC_SPEED:
            self._update_speed()

        # Logika ruchu
        if self.has_food:
            if not self._return_via_path(obstacles):
                self._return_to_nest(obstacles)
        else:
            # Sprawdź czy mrówka wraca do źródła jedzenia po śladzie
            if self.return_path and self.return_path_index is not None:
                if not self._return_to_food_source(obstacles):
                    # Jeśli dotarła do źródła, szukaj jedzenia
                    self._search_for_food(pheromones, foods, obstacles)
            else:
                # Normalne szukanie jedzenia
                self._search_for_food(pheromones, foods, obstacles)

        # Obsługa przeszkód
        if ENABLE_OBSTACLES:
            self._handle_obstacle_collision(obstacles)

        # Aktualizacja pozycji
        new_x = self.x + math.cos(self.angle) * self.speed
        new_y = self.y + math.sin(self.angle) * self.speed
        
        if not ENABLE_OBSTACLES or not self._position_collides_with_obstacles(new_x, new_y, obstacles):
            self.x = new_x
            self.y = new_y
        else:
            self._find_alternative_path(obstacles)

        # Ograniczenia planszy
        self.x = max(0, min(WINDOW_WIDTH, self.x))
        self.y = max(0, min(WINDOW_HEIGHT, self.y))

        # Aktualizacja pamięci
        self.memory.add_position(self.x, self.y)
        self.last_position = (self.x, self.y)
        
        # Sprawdzenie dotarcia do gniazda - usunięte, bo jest obsługiwane w _return_to_nest
        
    def _check_if_stuck(self):
        """Sprawdza czy mrówka nie jest zablokowana"""
        if not ENABLE_ADVANCED_NAVIGATION:
            return
            
        distance_moved = math.sqrt((self.x - self.last_position[0])**2 + 
                                 (self.y - self.last_position[1])**2)
        
        if distance_moved < 1:
            self.stuck_time += 1
            if self.stuck_time > 30:
                self.angle += random.uniform(-math.pi/2, math.pi/2)
                self.stuck_time = 0
        else:
            self.stuck_time = 0
            
    def _update_speed(self):
        """Aktualizuje prędkość mrówki"""
        if not ENABLE_DYNAMIC_SPEED:
            return
            
        base_speed = self.base_speed
        
        if self.has_food:
            base_speed *= 0.8
        elif self.specialization == 'scout':
            base_speed *= 1.2
            
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
                dx = self.x - (obstacle.x + obstacle.width/2)
                dy = self.y - (obstacle.y + obstacle.height/2)
                avoidance_angle = math.atan2(dy, dx)
                self.angle = avoidance_angle + random.uniform(-math.pi/4, math.pi/4)
                break
                
    def _find_alternative_path(self, obstacles: List[Obstacle]):
        """Znajduje alternatywną ścieżkę omijając przeszkody"""
        if not ENABLE_ADVANCED_NAVIGATION:
            return
            
        for i in range(8):
            test_angle = self.angle + (i * math.pi/4)
            test_x = self.x + math.cos(test_angle) * self.speed
            test_y = self.y + math.sin(test_angle) * self.speed
            
            if not self._position_collides_with_obstacles(test_x, test_y, obstacles):
                self.angle = test_angle
                return
                
        self.angle = random.uniform(0, 2 * math.pi)
        
    def _return_to_nest(self, obstacles: List[Obstacle] = None):
        """Logika powrotu do gniazda"""
        if obstacles is None:
            obstacles = []
            
        dx = self.nest.x - self.x
        dy = self.nest.y - self.y
        distance_to_nest = math.sqrt(dx*dx + dy*dy)
        
        if distance_to_nest < 20:
            # Mrówka dotarła do gniazda
            self.nest.store_food(self.food_amount)
            self.food_amount = 0
            self.has_food = False
            
            # Od razu wróć po śladzie feromonowym do źródła jedzenia
            if self.return_path and len(self.return_path) > 0:
                # Resetuj indeks ścieżki i idź z powrotem
                self.return_path_index = len(self.return_path) - 1
                # Ustaw kąt w kierunku pierwszego punktu ścieżki powrotu
                target = self.return_path[self.return_path_index]
                dx = target[0] - self.x
                dy = target[1] - self.y
                self.angle = math.atan2(dy, dx)
            else:
                # Jeśli nie ma ścieżki, wędruj losowo
                self.angle = random.uniform(0, 2 * math.pi)
        else:
            target_angle = math.atan2(dy, dx)
            angle_diff = self._normalize_angle_diff(target_angle)
            self.angle += angle_diff * 0.1
            
    def _search_for_food(self, pheromones: List[Pheromone], foods: List[Food], obstacles: List[Obstacle] = None):
        """Logika poszukiwania jedzenia"""
        if obstacles is None:
            obstacles = []
            
        if self.just_picked_food:
            return

        # Sprawdź znane lokalizacje jedzenia
        if ENABLE_ANT_MEMORY and self.memory.food_locations:
            for food_x, food_y in self.memory.food_locations:
                dx = food_x - self.x
                dy = food_y - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                if distance < 50:
                    target_angle = math.atan2(dy, dx)
                    angle_diff = self._normalize_angle_diff(target_angle)
                    self.angle += angle_diff * 0.3
                    return

        # Sprawdź jedzenie w pobliżu
        for food in foods:
            if not food.is_empty():
                dx = food.x - self.x
                dy = food.y - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                if distance < 15:
                    taken = food.take_food(self.max_food_capacity)
                    if taken > 0:
                        self.food_amount = taken
                        self.waiting_after_food = True
                        self.wait_counter = 0
                        self.memory.add_food_location(food.x, food.y)
                        return

        # Sprawdź feromony jedzeniowe w pobliżu
        nearby_pheromones = []
        for pheromone in pheromones:
            if pheromone.pheromone_type == 'food' and pheromone.strength > 0.1:
                dx = pheromone.x - self.x
                dy = pheromone.y - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                if distance < NAVIGATION_RANGE:
                    strength = pheromone.get_gradient_strength(distance)
                    if strength > 0.05:
                        nearby_pheromones.append((pheromone, distance, strength))

        # Jeśli są feromony w pobliżu, idź w kierunku przeciwnym do gniazda
        if nearby_pheromones:
            # Znajdź feromon w kierunku przeciwnym do gniazda
            best_pheromone = None
            best_score = -1
            
            for pheromone, distance, strength in nearby_pheromones:
                # Oblicz kierunek do feromonu
                dx_to_pheromone = pheromone.x - self.x
                dy_to_pheromone = pheromone.y - self.y
                
                # Oblicz kierunek do gniazda
                dx_to_nest = self.nest.x - self.x
                dy_to_nest = self.nest.y - self.y
                
                # Oblicz iloczyn skalarny (im bardziej przeciwny kierunek, tym lepszy)
                dot_product = dx_to_pheromone * dx_to_nest + dy_to_pheromone * dy_to_nest
                
                # Normalizuj odległość
                normalized_score = dot_product / (distance + 1)  # +1 żeby uniknąć dzielenia przez 0
                
                if normalized_score < best_score:  # Szukamy najmniejszego (najbardziej ujemnego)
                    best_score = normalized_score
                    best_pheromone = pheromone
            
            if best_pheromone:
                # Idź w stronę wybranego feromonu
                target_angle = math.atan2(best_pheromone.y - self.y, best_pheromone.x - self.x)
                target_angle += random.uniform(-0.2, 0.2)
                
                angle_diff = self._normalize_angle_diff(target_angle)
                self.angle += angle_diff * 0.2
                return
            
        # Jeśli nie ma feromonów, wędruj losowo
        self._wander(obstacles)
            
    def _wander(self, obstacles: List[Obstacle] = None):
        """Losowe wędrowanie mrówki"""
        if obstacles is None:
            obstacles = []
            
        self.wander_angle += random.uniform(-self.wander_change, self.wander_change)
        
        if random.random() < 0.033:
            self.wander_angle = random.uniform(0, 2 * math.pi)
            
        wander_x = self.x + math.cos(self.wander_angle) * self.wander_distance
        wander_y = self.y + math.sin(self.wander_angle) * self.wander_distance
        wander_x += random.uniform(-self.wander_radius, self.wander_radius)
        wander_y += random.uniform(-self.wander_radius, self.wander_radius)
        
        if ENABLE_OBSTACLES:
            for obstacle in obstacles:
                if obstacle.collides_with(wander_x, wander_y):
                    self.wander_angle = random.uniform(0, 2 * math.pi)
                    wander_x = self.x + math.cos(self.wander_angle) * self.wander_distance
                    wander_y = self.y + math.sin(self.wander_angle) * self.wander_distance
                    break
        
        dx = wander_x - self.x
        dy = wander_y - self.y
        target_angle = math.atan2(dy, dx)
        
        if ENABLE_ADVANCED_NAVIGATION:
            test_x = self.x + math.cos(target_angle) * self.speed
            test_y = self.y + math.sin(target_angle) * self.speed
            if self._position_collides_with_obstacles(test_x, test_y, obstacles):
                target_angle = random.uniform(0, 2 * math.pi)
        
        angle_diff = self._normalize_angle_diff(target_angle)
        self.angle += angle_diff * 0.1
        
    def drop_pheromone(self, pheromones: List[Pheromone]):
        """Zostawia feromon na planszy tylko gdy niesie jedzenie"""
        if self.has_food and random.random() < self.pheromone_drop_rate:
            strength = 1.0 * PHEROMONE_STRENGTH_MULTIPLIER
            
            if ENABLE_ANT_SPECIALIZATION:
                if self.specialization == 'scout':
                    strength *= 1.5
                elif self.specialization == 'collector':
                    strength *= 1.2
                    
            pheromones.append(Pheromone(int(self.x), int(self.y), strength, 'food'))
            
    def draw(self, screen):
        """Rysuje mrówkę"""
        if self.has_food:
            color = ORANGE
        elif ENABLE_ANT_SPECIALIZATION:
            if self.specialization == 'scout':
                color = (255, 0, 255)
            elif self.specialization == 'collector':
                color = (0, 255, 255)
            elif self.specialization == 'guard':
                color = (255, 255, 0)
            else:
                color = RED
        else:
            color = RED
            
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        
        # Kierunek ruchu
        end_x = self.x + math.cos(self.angle) * 8
        end_y = self.y + math.sin(self.angle) * 8
        pygame.draw.line(screen, BLACK, (self.x, self.y), (end_x, end_y), 2)
        
        # Specjalizacja
        if ENABLE_ANT_SPECIALIZATION and self.specialization != 'general':
            spec_x = int(self.x) + 6
            spec_y = int(self.y) - 6
            pygame.draw.rect(screen, BLACK, (spec_x, spec_y, 3, 3))

    def _return_to_food_source(self, obstacles: List[Obstacle] = None) -> bool:
        """Wraca do źródła jedzenia po śladzie feromonowym"""
        if obstacles is None:
            obstacles = []
            
        if not self.return_path or self.return_path_index is None:
            return False
            
        if self.return_path_index < 0:
            # Dotarła do źródła jedzenia
            self.return_path = []
            self.return_path_index = None
            return False
            
        # Idź do następnego punktu ścieżki
        target = self.return_path[self.return_path_index]
        dx = target[0] - self.x
        dy = target[1] - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 3:
            # Przejdź do następnego punktu
            self.return_path_index -= 1
        else:
            # Idź w kierunku punktu
            target_angle = math.atan2(dy, dx)
            angle_diff = self._normalize_angle_diff(target_angle)
            self.angle += angle_diff * 0.15
            
        return True

class AntSimulator:
    """Główna klasa symulatora"""
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Symulator Mrówek")
        self.clock = pygame.time.Clock()
        
        self.nest = Nest(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.ants = []
        self.foods = []
        self.pheromones = []
        self.obstacles = []
        
        # Stwórz przeszkody
        if ENABLE_OBSTACLES:
            self._create_obstacles()
            
        # Stwórz początkowe mrówki
        self._create_initial_ants()
        
        # Stwórz jedzenie
        self._spawn_food()

    def _create_obstacles(self):
        """Tworzy początkowe przeszkody"""
        for _ in range(OBSTACLE_COUNT):
            x = random.randint(100, WINDOW_WIDTH - 100)
            y = random.randint(100, WINDOW_HEIGHT - 100)
            w = random.randint(OBSTACLE_MIN_SIZE, OBSTACLE_MAX_SIZE)
            h = random.randint(OBSTACLE_MIN_SIZE, OBSTACLE_MAX_SIZE)
            self.obstacles.append(Obstacle(x, y, w, h))

    def _create_initial_ants(self):
        """Tworzy początkowe mrówki"""
        for _ in range(50):
            x = self.nest.x + random.uniform(-50, 50)
            y = self.nest.y + random.uniform(-50, 50)
            self.ants.append(Ant(int(x), int(y), self.nest))
        
    def _spawn_food(self):
        """Tworzy nowe jedzenie na planszy"""
        # Stwórz jeden duży punkt jedzenia
        attempts = 0
        while attempts < 50:
            x = random.randint(100, WINDOW_WIDTH - 100)
            y = random.randint(100, WINDOW_HEIGHT - 100)
            
            # Jedzenie daleko od gniazda
            nest_x, nest_y = self.nest.x, self.nest.y
            min_dist = 300
            if math.sqrt((x-nest_x)**2 + (y-nest_y)**2) < min_dist:
                attempts += 1
                continue
                
            valid_position = True
            if ENABLE_OBSTACLES:
                for obstacle in self.obstacles:
                    if obstacle.collides_with(x, y, 15):
                        valid_position = False
                        break
                        
            if valid_position:
                amount = random.randint(2000, 4000)  # 10x więcej jedzenia
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
        self.pheromones = [p for p in self.pheromones if p.strength > 0.01]
        for pheromone in self.pheromones:
            pheromone.update()
                
            
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
                if alpha > 10:
                    pygame.draw.circle(self.screen, color, (pheromone.x, pheromone.y), 2)
            except (ValueError, TypeError):
                continue
                
        # Rysuj jedzenie
        for food in self.foods:
            color = food.get_color()
            pygame.draw.circle(self.screen, color, (food.x, food.y), 50)
            pygame.draw.circle(self.screen, BLACK, (food.x, food.y), 50, 2)
            
        # Rysuj gniazdo
        self.nest.draw(self.screen)
        
        # Rysuj mrówki
        for ant in self.ants:
            ant.draw(self.screen)
            
        # Wyświetl statystyki
        self._draw_stats()
        
        pygame.display.flip()

    def _draw_stats(self):
        """Rysuje statystyki na ekranie"""
        font = pygame.font.Font(None, 36)
        stats_text = f"Mrówki: {len(self.ants)} | Jedzenie: {len(self.foods)} | Feromony: {len(self.pheromones)}"
        if ENABLE_OBSTACLES:
            stats_text += f" | Przeszkody: {len(self.obstacles)}"
        text_surface = font.render(stats_text, True, BLACK)
        self.screen.blit(text_surface, (10, 10))
        
        # Informacje o funkcjach
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
        
    def _handle_events(self):
        """Obsługuje zdarzenia pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    self._add_ants(10)
                elif event.key == pygame.K_f:
                    self._spawn_food()
                elif event.key == pygame.K_o:
                    self._add_obstacle()
                elif event.key == pygame.K_r:
                    self._reset_obstacles()
        return True

    def _add_ants(self, count: int):
        """Dodaje nowe mrówki"""
        for _ in range(count):
            x = self.nest.x + random.uniform(-50, 50)
            y = self.nest.y + random.uniform(-50, 50)
            self.ants.append(Ant(int(x), int(y), self.nest))

    def _add_obstacle(self):
        """Dodaje nową przeszkodę"""
        if ENABLE_OBSTACLES:
            x = random.randint(100, WINDOW_WIDTH - 100)
            y = random.randint(100, WINDOW_HEIGHT - 100)
            w = random.randint(OBSTACLE_MIN_SIZE, OBSTACLE_MAX_SIZE)
            h = random.randint(OBSTACLE_MIN_SIZE, OBSTACLE_MAX_SIZE)
            self.obstacles.append(Obstacle(x, y, w, h))

    def _reset_obstacles(self):
        """Resetuje przeszkody"""
        if ENABLE_OBSTACLES:
            self.obstacles.clear()
            self._create_obstacles()
        
    def run(self):
        """Główna pętla gry"""
        running = True
        while running:
            running = self._handle_events()
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    simulator = AntSimulator()
    simulator.run() 