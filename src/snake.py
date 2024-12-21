import pygame
import random
import json
from gridElements import Block

WIDTH: int = 600
HEIGHT: int = 600  # Size of the game window
GRID_SIZE: int = 20  # Size of each block (both snake body and apple)
ROWS: int = WIDTH // GRID_SIZE
COLS: int = HEIGHT // GRID_SIZE  # Grid dimensions

WHITE: tuple[int, int, int] = (255, 255, 255)
BLACK: tuple[int, int, int] = (0, 0, 0)

class Apple:
    def __init__(self, coord: tuple[int, int]):
        self.x: int
        self.y: int
        self.x, self.y = coord
        self.color: tuple[int, int, int] = self._generate_random_color()

    def __repr__(self) -> str:
        return f"Apple(x={self.x}, y={self.y}, color={self.color})"

    def reposition(self) -> None:
        self.x = random.randint(0, COLS - 1)
        self.y = random.randint(0, ROWS - 1)
        self.color = self._generate_random_color()

    def _generate_random_color(self) -> tuple[int, int, int]:
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

class SnakeBodyBlock:
    def __init__(self, coord: tuple[int, int]):
        self.x: int
        self.y: int
        self.x, self.y = coord

    def __repr__(self) -> str:
        return f"Block(x={self.x}, y={self.y})"

class Snake:
    def __init__(self, path: str, initial_position: tuple[int, int]):
        with open(path, "r") as file:
            data: dict = json.load(file)

        blocks_in_cell: int = data["blocks_in_cell"]
        self.map_width: int = data["maze_width_in_cells"] * blocks_in_cell
        self.map_height: int = data["maze_height_in_cells"] * blocks_in_cell

        self.body: list[SnakeBodyBlock] = [SnakeBodyBlock(initial_position)]
        self.body_colors: list[tuple[int, int, int]] = [self._generate_random_color()]
        self.direction: tuple[int, int] = (0, 0)
        
        self.in_river: bool = False
        self.speed_in_river: int = data.get("rivers_data", {})["speed_in_river"]
        self.river_counter: int = 0

        self.ghost_mode: bool = False
        self.tp_next_move: bool = False
        self.skip_next_move: bool = False
        self.move_skip_counter: int = 0

    def move(self) -> None:
        if self.tp_next_move:
            self.teleport_move()
            return  
        if self.skip_next_move:
            self.skip_next_move = False
            self.move_skip_counter += 1
            return
        if self.in_river:
            self.river_counter += 1
            if self.river_counter % self.speed_in_river != 0:
                return
        
        head: SnakeBodyBlock = self.body[0]
        new_x: int = head.x + self.direction[0] 
        new_y: int = head.y + self.direction[1] 
        new_head: SnakeBodyBlock = SnakeBodyBlock((new_x, new_y))
        self.body.insert(0, new_head)
        self.body.pop()

    def grow(self, apple: Apple) -> None:
        last_block: SnakeBodyBlock = self.body[-1]
        self.body.append(SnakeBodyBlock((last_block.x, last_block.y)))
        self.body_colors.append(apple.color)

    def change_direction(self, new_direction: tuple[int, int]) -> None:
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction
        else: 
            self.direction = (0, 0)

    def check_apple_collision(self, apple: Apple) -> None:
        head: SnakeBodyBlock = self.body[0]
        if int(head.x) == apple.x and int(head.y) == apple.y:
            self.grow(apple)
            apple.reposition()

    def check_snake_collision(self, snake_block: Block, next_step_block: Block) -> None:
        head: SnakeBodyBlock = self.body[0]
        for i in range(1, len(self.body)):
           if self.body[i].x == head.x + self.direction[0] and \
            self.body[i].y == head.y + self.direction[1]:
                self.skip_next_move = True
                return
           
        if self.direction == (0, 0) or self.ghost_mode:
            return
        if not next_step_block:
            self.skip_next_move = True
            return

        self.in_river = False
        
        snake_block_walls: list[str] = snake_block.get_walls()
        next_block_walls: list[str] = next_step_block.get_walls() 

        snake_block_walls = snake_block_walls if snake_block_walls else []
        next_block_walls = next_block_walls if next_block_walls else []
        if snake_block_walls or next_block_walls:
            if self.direction[0] == 1 and ("right" in snake_block_walls or "left" in next_block_walls):
                self.skip_next_move = True
            elif self.direction[0] == -1 and ("left" in snake_block_walls or "right" in next_block_walls):
                self.skip_next_move = True
            
            if self.direction[1] == 1 and ("down" in snake_block_walls or "top" in next_block_walls):
                self.skip_next_move = True
            elif self.direction[1] == -1 and ("top" in snake_block_walls or "down" in next_block_walls):
                self.skip_next_move = True

        next_block_traits: list[str] = next_step_block.get_traits()
        if not next_block_traits:
            return
        
        if "lava" in next_block_traits:
            self.skip_next_move = True
        
        if "forest" in next_block_traits:
            self.skip_next_move = True
        
        snake_block_traits: list[str] = snake_block.get_traits()
        
        if snake_block_traits and "river" in snake_block_traits:
            self.in_river = True
    
    def teleport(self) -> None:
        self.tp_next_move = True

    def teleport_move(self) -> None:
        self.tp_next_move = False
        head: SnakeBodyBlock = self.body[0]
        tx: int = head.x + 2 * self.direction[0]
        ty: int = head.y + 2 * self.direction[1]

        if self.can_teleport_to_new_location(tx, ty):
            head.x = tx
            head.y = ty
        for i in range(1, len(self.body)):
            self.body[i].x = head.x
            self.body[i].y = head.y
    
    def can_teleport_to_new_location(self, x: int, y: int) -> bool:
        if x < 0 or y < 0 or x >= self.map_width or y >= self.map_height:
            return False
        
        return True

    def check_pygame_events(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.change_direction((0, -1))
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.change_direction((0, 1))
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.change_direction((-1, 0))
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.change_direction((1, 0))
            elif event.key == pygame.K_t:
                self.teleport()
            elif event.key == pygame.K_g:
                self.ghost_mode = not self.ghost_mode

    def _generate_random_color(self) -> tuple[int, int, int]:
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def __repr__(self) -> str:
        return f"Snake(body={self.body})"

def game_loop() -> None:
    clock: pygame.time.Clock = pygame.time.Clock()
    snake: Snake = Snake("./res/config.json", (5, 5))
    apple: Apple = Apple((random.randint(0, COLS - 1), random.randint(0, ROWS - 1)))

    running: bool = True
    
    while running:
        screen.fill(BLACK)  

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            snake.check_pygame_events(event)

        snake.move()
        snake.check_apple_collision(apple)

        for block, color in zip(snake.body, snake.body_colors):
            x: int = block.x * GRID_SIZE
            y: int = block.y * GRID_SIZE
            pygame.draw.rect(screen, color, (x, y, GRID_SIZE, GRID_SIZE))

        pygame.draw.rect(screen, apple.color, (apple.x * GRID_SIZE, apple.y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        pygame.display.update()
        clock.tick(5)  
        
if __name__ == "__main__":
    screen: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Smooth Snake Game')
    pygame.init()
    game_loop()
    pygame.quit()
