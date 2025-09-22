import pygame
import random
import time

# Initialize Pygame
pygame.init()

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

# Initialize game window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Snake Game')

class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = 'RIGHT'
        self.grow = False

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
        
        # Insert new head
        self.body.insert(0, new_head)
        
        # Remove tail if not growing
        if not self.grow:
            self.body.pop()
        self.grow = False

    def check_collision(self):
        head = self.body[0]
        # Check wall collision
        if (head[0] < 0 or head[0] >= GRID_WIDTH or 
            head[1] < 0 or head[1] >= GRID_HEIGHT):
            return True
        
        # Check self collision
        if head in self.body[1:]:
            return True
        
        return False

class Food:
    def __init__(self):
        self.position = self.generate_position()

    def generate_position(self):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            return (x, y)

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_over = False
        self.clock = pygame.time.Clock()

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
        return True

    def update(self):
        if not self.game_over:
            self.snake.move()
            
            # Check for collision with food
            if self.snake.body[0] == self.food.position:
                self.snake.grow = True
                self.food = Food()
                self.score += 1
            
            # Check for collision with walls or self
            if self.snake.check_collision():
                self.game_over = True

    def draw(self):
        window.fill(BLACK)
        
        # Draw snake
        for segment in self.snake.body:
            pygame.draw.rect(window, GREEN, 
                           (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, 
                            GRID_SIZE - 2, GRID_SIZE - 2))
        
        # Draw food
        pygame.draw.rect(window, RED,
                        (self.food.position[0] * GRID_SIZE, 
                         self.food.position[1] * GRID_SIZE,
                         GRID_SIZE - 2, GRID_SIZE - 2))
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        window.blit(score_text, (10, 10))
        
        # Draw game over message
        if self.game_over:
            game_over_text = font.render('Game Over! Press R to Restart', True, WHITE)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
            window.blit(game_over_text, text_rect)
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            
            if not self.game_over:
                self.update()
            else:
                # Check for restart
                keys = pygame.key.get_pressed()
                if keys[pygame.K_r]:
                    self.__init__()
            
            self.draw()
            self.clock.tick(10)  # Control game speed

def main():
    game = Game()
    game.run()
    pygame.quit()

if __name__ == "__main__":
    main()