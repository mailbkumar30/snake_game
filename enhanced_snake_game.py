import pygame
import random
import time
import json
import os
from pygame import mixer

# Initialize Pygame and mixer
pygame.init()
mixer.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)
DARK_GREEN = (0, 100, 0)

# Fruit Colors
APPLE_RED = (255, 59, 59)
BANANA_YELLOW = (255, 225, 53)
ORANGE_COLOR = (255, 159, 41)
BLUEBERRY_COLOR = (41, 128, 255)
GRAPE_COLOR = (155, 89, 182)

# UI Colors
BACKGROUND_COLOR = (15, 15, 30)
HEADER_COLOR = (30, 30, 50)
BORDER_COLOR = (50, 50, 80)

# Initialize game window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Snake & Fruits - A Tasty Adventure')

# Load or create high score
def load_high_score():
    try:
        with open('high_score.json', 'r') as f:
            return json.load(f)['high_score']
    except:
        return 0

def save_high_score(score):
    with open('high_score.json', 'w') as f:
        json.dump({'high_score': score}, f)

class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = 'RIGHT'
        self.grow = False
        self.color = GREEN
        self.head_color = DARK_GREEN

    def move(self):
        head_x, head_y = self.body[0]
        
        if self.direction == 'UP':
            new_head = (head_x, head_y - 1)
        elif self.direction == 'DOWN':
            new_head = (head_x, head_y + 1)
        elif self.direction == 'LEFT':
            new_head = (head_x - 1, head_y)
        else:  # RIGHT
            new_head = (head_x + 1, head_y)
        
        self.body.insert(0, new_head)
        self.wrap_position()
        
        if not self.grow:
            self.body.pop()
        self.grow = False

    def check_collision(self):
        head = self.body[0]
        # Only check for self collision, not wall collision
        if head in self.body[1:]:
            return True
        
        return False
        
    def wrap_position(self):
        head = list(self.body[0])
        # Wrap horizontally
        if head[0] < 0:
            head[0] = GRID_WIDTH - 1
        elif head[0] >= GRID_WIDTH:
            head[0] = 0
        # Wrap vertically, considering header space
        if head[1] < 2:
            head[1] = GRID_HEIGHT - 1
        elif head[1] >= GRID_HEIGHT:
            head[1] = 2
        self.body[0] = tuple(head)

class Food:
    def __init__(self):
        self.position = self.generate_position()
        self.fruit_types = [
            {'name': 'apple', 'color': APPLE_RED, 'points': 1},
            {'name': 'banana', 'color': BANANA_YELLOW, 'points': 2},
            {'name': 'orange', 'color': ORANGE_COLOR, 'points': 3},
            {'name': 'blueberry', 'color': BLUEBERRY_COLOR, 'points': 4},
            {'name': 'grape', 'color': GRAPE_COLOR, 'points': 5}
        ]
        self.set_random_fruit()
        self.special = False
        self.special_timer = 0

    def generate_position(self):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(2, GRID_HEIGHT - 1)  # Adjusted for header
            return (x, y)

    def set_random_fruit(self):
        self.current_fruit = random.choice(self.fruit_types)
        self.color = self.current_fruit['color']
        self.points = self.current_fruit['points']

    def make_special(self):
        self.special = True
        self.color = GOLD
        self.points *= 2
        self.special_timer = time.time()

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.high_score = load_high_score()
        self.game_over = False
        self.clock = pygame.time.Clock()
        self.start_time = time.time()
        self.elapsed_time = 0
        self.speed = 6  # Slower initial speed
        self.special_food_chance = 0.1
        
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.snake.direction != 'DOWN':
                    self.snake.direction = 'UP'
                elif event.key == pygame.K_DOWN and self.snake.direction != 'UP':
                    self.snake.direction = 'DOWN'
                elif event.key == pygame.K_LEFT and self.snake.direction != 'RIGHT':
                    self.snake.direction = 'LEFT'
                elif event.key == pygame.K_RIGHT and self.snake.direction != 'LEFT':
                    self.snake.direction = 'RIGHT'
                elif event.key == pygame.K_SPACE and self.game_over:
                    self.__init__()
        return True

    def update(self):
        if not self.game_over:
            self.elapsed_time = int(time.time() - self.start_time)
            self.snake.move()
            
            # Check for food collision
            if self.snake.body[0] == self.food.position:
                self.snake.grow = True
                self.score += self.food.points
                
                # Update high score
                if self.score > self.high_score:
                    self.high_score = self.score
                    save_high_score(self.high_score)
                
                # Create new food
                self.food = Food()
                if random.random() < self.special_food_chance:
                    self.food.make_special()
                
                # Increase speed more gradually
                self.speed = min(12, 6 + (self.score // 10))  # Slower max speed and gentler increase
            
            # Check for special food timeout
            if self.food.special and time.time() - self.food.special_timer > 5:
                self.food = Food()
            
            # Check for collision
            if self.snake.check_collision():
                self.game_over = True

    def draw_header(self):
        # Draw header background
        pygame.draw.rect(window, HEADER_COLOR, (0, 0, WINDOW_WIDTH, GRID_SIZE * 2))
        pygame.draw.line(window, BORDER_COLOR, (0, GRID_SIZE * 2), 
                        (WINDOW_WIDTH, GRID_SIZE * 2), 2)

        # Draw scores and time
        font = pygame.font.Font(None, 36)
        
        # Current Score
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        window.blit(score_text, (10, 10))
        
        # High Score
        high_score_text = font.render(f'High Score: {self.high_score}', True, GOLD)
        high_score_rect = high_score_text.get_rect(midtop=(WINDOW_WIDTH/2, 10))
        window.blit(high_score_text, high_score_rect)
        
        # Time
        time_text = font.render(f'Time: {self.elapsed_time}s', True, WHITE)
        time_rect = time_text.get_rect(topright=(WINDOW_WIDTH - 10, 10))
        window.blit(time_text, time_rect)

    def draw(self):
        # Fill background
        window.fill(BACKGROUND_COLOR)
        
        # Draw header
        self.draw_header()
        
        # Draw snake
        for i, segment in enumerate(self.snake.body):
            color = self.snake.head_color if i == 0 else self.snake.color
            pygame.draw.rect(window, color,
                           (segment[0] * GRID_SIZE, 
                            segment[1] * GRID_SIZE,
                            GRID_SIZE - 2, GRID_SIZE - 2))
        
        # Draw food
        pygame.draw.rect(window, self.food.color,
                        (self.food.position[0] * GRID_SIZE,
                         self.food.position[1] * GRID_SIZE,
                         GRID_SIZE - 2, GRID_SIZE - 2))
        
        # Draw game over
        if self.game_over:
            font = pygame.font.Font(None, 48)
            game_over_text = font.render('Game Over!', True, RED)
            score_text = font.render(f'Final Score: {self.score}', True, WHITE)
            restart_text = font.render('Press SPACE to Restart', True, WHITE)
            
            text_y = WINDOW_HEIGHT/2 - 60
            for text in [game_over_text, score_text, restart_text]:
                text_rect = text.get_rect(center=(WINDOW_WIDTH/2, text_y))
                window.blit(text, text_rect)
                text_y += 40
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            
            if not self.game_over:
                self.update()
            
            self.draw()
            self.clock.tick(self.speed)  # Dynamic game speed

def main():
    game = Game()
    game.run()
    pygame.quit()

if __name__ == "__main__":
    main()