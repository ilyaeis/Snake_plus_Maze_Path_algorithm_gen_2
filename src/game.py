import json
import pygame
import math
import random

from snake import Snake, SnakeBodyBlock, Apple
from map import Map
from gridElements import Block 
from pathSearchers import BFS
class Game:
    def __init__(self, path: str) -> None:
        self.load_config(path)
        self.initialize_game_elements(path)
        self.initialize_canvases()

    def load_config(self, path: str) -> None:
        with open(path, "r") as file:
            data: dict = json.load(file)

        self.blocks_in_cell: int = data["blocks_in_cell"]
        self.map_width: int = data["maze_width_in_cells"] * self.blocks_in_cell
        self.map_height: int = data["maze_height_in_cells"] * self.blocks_in_cell

        self.screen_width: int = data["screen_width_px"]
        self.screen_height: int = data["screen_height_px"]

        self.block_size: int = data["block_size_px"]
        self.tree_size: float = data["tree_size"]
        self.apple_count: int = data["apple_count"]

        self.colors: dict = data.get("colors", {})
        self.images: dict = data.get("images", {})

    def initialize_game_elements(self, path: str) -> None:
        maps_obj: Map = Map(path)
        self.map: list[list[Block]] = maps_obj.map
        start_location: tuple[int, int] = self.find_snake_location()
        if start_location:
            self.snake: Snake = Snake(path, start_location)
        else:
            print("No location to start, please re-start! :)")
            return
        self.path_searcher = BFS(self.map)
        self.apples: list[Apple] = []
        self.generate_apples(self.apple_count, start_location)
        self.screen: pygame.Surface = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.exit_blocks: set[Block] = set()

    def initialize_canvases(self) -> None:
        self.background_canvas: pygame.Surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.path_canvas: pygame.Surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.apple_count_canvas: pygame.Surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.terrain_canvas: pygame.Surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.maze_canvas: pygame.Surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.apple_canvas: pygame.Surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.snake_canvas: pygame.Surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.tree_crown_canvas: pygame.Surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.tree_base_canvas: pygame.Surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
    
    def find_snake_location(self) -> tuple[int, int]:
        for x in range(self.map_width // 4, 3 * self.map_width // 4):
            for y in range(self.map_height // 4, 3 * self.map_height // 4):
                if not self.map[y][x].get_walls() and not self.map[y][x].get_traits() and not self.neighbours_has_traits(x, y):
                    return (x, y)
        return None
    
    def generate_apples(self, apple_count: int, snake_start: tuple[int, int]) -> None:
        apples_coord: set[tuple[int, int]] = set()
        for _ in range(apple_count):
            x: int
            y: int
            x, y = self.find_apple_location()
            while (x, y) == snake_start or (x, y) in apples_coord or self.other_apples_nearby(x, y, 5):
                x, y = self.find_apple_location()
            self.apples.append(Apple((x, y)))
            apples_coord.add((x, y))

    def other_apples_nearby(self, x: int, y: int, distance: int) -> bool:
        for apple in self.apples:
            if abs(apple.x - x) <= distance and abs(apple.y - y) <= distance:
                return True
        return False
    
    def find_apple_location(self) -> tuple[int, int]:
        for _ in range(100):
            x: int = random.randint(0, self.map_width - 1)
            y: int = random.randint(0, self.map_height - 1)
            if not self.map[y][x].get_walls() and not self.map[y][x].get_traits() and not self.neighbours_has_traits(x, y):
                return (x, y)
        return None
    
    def create_exit(self) -> None:
        border_length: int = 2 * (self.map_width + self.map_height) - 4
        position: int = random.randint(0, border_length - 1)
        const: int = 0
        if position < self.map_width:
            x: int = position
            y: int = 0
            const = y
        elif position < self.map_width + self.map_height - 1:
            x: int = self.map_width - 1
            y: int = position - self.map_width + 1
            const = x
        elif position < 2 * self.map_width + self.map_height - 2:
            x: int = 2 * self.map_width + self.map_height - 3 - position
            y: int = self.map_height - 1
            const = y
        else:
            x: int = 0
            y: int = border_length - position - 1
            const = x

        if x > self.map_width - self.blocks_in_cell - 1 and x != const:
            x = self.map_width - self.blocks_in_cell - 1
        if y > self.map_height - self.blocks_in_cell - 1 and y != const:
            y = self.map_height - self.blocks_in_cell - 1
        
        for l in range(0, self.blocks_in_cell):
            if const == x:
                self.map[y + l][x].walls = {"top": False, "down": False, "left": False, "right": False}
                self.exit_blocks.add(self.map[y + l][x])
            elif const == y:
                self.map[y][x + l].walls = {"top": False, "down": False, "left": False, "right": False}
                self.exit_blocks.add(self.map[y][x + l])
            else:
                print("Error")
    
    def neighbours_has_traits(self, x: int, y: int) -> bool:
        directions: list[list[int]] = [
            [-1, -1], [0, -1], [1, -1],
            [-1, 0],          [1, 0],
            [-1, 1], [0, 1], [1, 1],
        ]

        neighbours_has_traits: bool = False
        for dx, dy in directions:
            nx: int = min(max(0, x + dx), self.map_width - 1)
            ny: int = min(max(0, y + dy), self.map_height - 1)

            if self.map[ny][nx].get_traits() is not None:
                neighbours_has_traits = True
                break

        return neighbours_has_traits

    def update_world_canvas(self) -> None:
        self.background_canvas.fill((0, 0, 0, 0))
        self.terrain_canvas.fill((0, 0, 0, 0))
        self.maze_canvas.fill((0, 0, 0, 0))
        self.apple_canvas.fill((0, 0, 0, 0))
        self.tree_crown_canvas.fill((0, 0, 0, 0))
        self.tree_base_canvas.fill((0, 0, 0, 0))

        wall_color: str = self.colors["maze_walls"]
        seen_map: list[list[Block]] = self.get_map_slice()
        for y in range(len(seen_map)):
            for x in range(len(seen_map[y])):
                block: Block = seen_map[y][x]

                bx: int
                by: int
                bx, by = self.block_pos_relative((block.x, block.y))
                apple: Apple = self.get_apple(block.x, block.y)
                if apple:
                    pygame.draw.rect(self.apple_canvas, apple.color, (bx, by, self.block_size, self.block_size))
                
                active_traits: list[str] = block.get_traits()  
                color: tuple = self.generate_height_color(block)
                pygame.draw.rect(self.background_canvas, color, (bx + 1, by + 1, self.block_size - 2, self.block_size - 2))
                
                if active_traits:
                    if "forest" in active_traits:
                        crown_size: float = self.block_size * self.tree_size
                        margin_px: float = 0.5 * (1 - self.tree_size) * self.block_size
                        pygame.draw.ellipse(self.tree_crown_canvas, self.colors["tree_crown"], (bx + margin_px, by + margin_px, crown_size, crown_size))
                        pygame.draw.rect(self.tree_base_canvas, self.colors["forest"], (bx + 1, by + 1, self.block_size - 2, self.block_size - 2))
                    for trait in active_traits:
                        color = self.colors[trait]
                    pygame.draw.rect(self.terrain_canvas, color, (bx, by, self.block_size, self.block_size))

                if block.walls["top"]:
                    pygame.draw.line(self.maze_canvas, wall_color, (bx, by), (bx + self.block_size, by), 1)
                if block.walls["down"]:
                    pygame.draw.line(self.maze_canvas, wall_color, (bx, by + self.block_size), (bx + self.block_size, by + self.block_size), 1)
                if block.walls["left"]:
                    pygame.draw.line(self.maze_canvas, wall_color, (bx, by), (bx, by + self.block_size), 1)
                if block.walls["right"]:
                    pygame.draw.line(self.maze_canvas, wall_color, (bx + self.block_size, by), (bx + self.block_size, by + self.block_size), 1)
        self.draw_exit()

    def get_apple(self, x: int, y: int) -> Apple:
        for apple in self.apples:
            if apple.x == x and apple.y == y:
                return apple
        return None
    
    def get_map_slice(self) -> list[list[Block]]:
        head: SnakeBodyBlock = self.snake.body[0]

        blocks_in_width: int = math.ceil(self.screen_width / self.block_size) + 1
        blocks_in_height: int = math.ceil(self.screen_height / self.block_size) + 1

        start_x: int = min(len(self.map[0]) - blocks_in_width, max(0, head.x - blocks_in_width // 2))
        start_y: int = min(len(self.map) - blocks_in_height, max(0, head.y - blocks_in_height // 2))

        end_x: int = start_x + blocks_in_width
        end_y: int = start_y + blocks_in_height
        
        return [self.map[y][start_x:end_x] for y in range(start_y, end_y)]
    
    def generate_height_color(self, block: Block) -> tuple:
        color: tuple = self.colors["terrain"]
        adjusted_color: tuple = tuple(c * block.height for c in color)
        return adjusted_color
    
    def block_pos_relative(self, block: tuple[int, int]) -> tuple[int, int]:
        head: SnakeBodyBlock = self.snake.body[0]
        
        bx: int = block[0] * self.block_size
        by: int = block[1] * self.block_size 
        sx: int = head.x * self.block_size
        sy: int = head.y * self.block_size
        cx: int = self.screen_width / 2 - self.block_size // 2
        cy: int = self.screen_height / 2 - self.block_size // 2

        return (bx - (sx - cx), by - (sy - cy))

    def update_snake_canvas(self) -> None:
        self.snake_canvas.fill((0, 0, 0, 0))
        for i in range(len(self.snake.body)):
            block: SnakeBodyBlock = self.snake.body[i]
            snake_color: tuple[int, int, int] = self.snake.body_colors[i]
            x: int
            y: int
            x, y = self.block_pos_relative((block.x, block.y))
            pygame.draw.rect(self.snake_canvas, snake_color, (x, y, self.block_size, self.block_size))

    def update_apple_count_canvas(self) -> None:
        self.apple_count_canvas.fill((0, 0, 0, 0))
        if len(self.apples) == 0:
            self.create_exit() 
            return        
        font: pygame.font.Font = pygame.font.Font(None, self.screen_width)
        text: pygame.Surface = font.render(f"{len(self.apples)}", True, self.colors["text"][:3])
        text.set_alpha(self.colors["text"][3])
        text_rect = text.get_rect(center=(self.apple_count_canvas.get_width() / 2, self.apple_count_canvas.get_height() / 2))
        self.apple_count_canvas.blit(text, text_rect)
    
    def update_path_canvas(self):
        self.path_canvas.fill((0, 0, 0, 0))
        if self.path_searcher.path:
            for block in self.path_searcher.path:
                color: tuple[int, int, int] = (255, 0, 0, 100)
                x, y = self.block_pos_relative((block[0], block[1]))
                pygame.draw.rect(self.path_canvas, color, (x, y, self.block_size, self.block_size))

        elif self.path_searcher.longest_path:
            for block in self.path_searcher.longest_path:
                color: tuple[int, int, int] = (255, 0, 0, 100)
                x, y = self.block_pos_relative((block[0], block[1]))
                pygame.draw.rect(self.path_canvas, color, (x, y, self.block_size, self.block_size))
        
    def draw_exit(self) -> None:
        if not self.exit_blocks:
            return 
        list_exit: list[Block] = list(self.exit_blocks)
        image_size: int = self.block_size * len(list_exit)
        image_margin: int = self.block_size * int(len(list_exit) - 1)
        dx: int = list_exit[0].x - list_exit[1].x
        dy: int = list_exit[0].y - list_exit[1].y

        min_x: int = min([block.x for block in list_exit])
        min_y: int = min([block.y for block in list_exit])

        image: pygame.Surface = pygame.image.load(self.images["exit"]) 
        if dx == 0:
            if list_exit[0].x == 0:
                image = pygame.transform.rotate(image, 180)
        elif dy == 0:
            if list_exit[0].y == 0:
                image = pygame.transform.rotate(image, 90)
            else:
                image = pygame.transform.rotate(image, 270)

        image = pygame.transform.scale(image, (image_size, image_size))
        x: int
        y: int
        x, y = self.block_pos_relative((min_x, min_y))
        if dx == 0:
            if list_exit[0].x == 0:
                x -= image_margin
        elif dy == 0:
            if list_exit[0].y == 0:
                y -= image_margin
        self.background_canvas.blit(image, (x, y))

    def game_loop(self) -> None:
        clock: pygame.time.Clock = pygame.time.Clock()
        running: bool = True
        won: bool = False

        self.update_apple_count_canvas()

        while running:
                
            self.screen.fill(pygame.Color(self.colors["maze_path"]))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.snake.check_pygame_events(event)

            snake_block: Block = self.map[self.snake.body[0].y][self.snake.body[0].x]
            next_block: Block = None
            if (0 <= self.snake.body[0].y + self.snake.direction[1] < self.map_height) \
            and (0 <= self.snake.body[0].x + self.snake.direction[0] < self.map_width):
                next_block = self.map[self.snake.body[0].y + self.snake.direction[1]][self.snake.body[0].x + self.snake.direction[0]]
            
            if not next_block and snake_block in self.exit_blocks:
                running = False
                won = True

            self.snake.check_snake_collision(snake_block, next_block)
            self.snake.move()
            if self.apples:
                self.path_searcher.create_path(self.snake, self.apples)
            else:
                self.path_searcher.create_path(self.snake, self.exit_blocks)
                
            if self.snake.check_apples_collision(self.apples):
                self.update_apple_count_canvas()
            if self.snake.lost():
                running = False
            
            self.screen.fill(pygame.Color(self.colors["maze_path"]))

            self.update_world_canvas()
            self.update_snake_canvas()
            self.update_path_canvas()
            
            self.screen.blit(self.background_canvas, (0, 0))
            self.screen.blit(self.apple_count_canvas, (0, 0))
            self.screen.blit(self.terrain_canvas, (0, 0))
            self.screen.blit(self.snake_canvas, (0, 0))
            self.screen.blit(self.apple_canvas, (0, 0))
            self.screen.blit(self.maze_canvas, (0, 0))
            self.screen.blit(self.tree_crown_canvas, (0, 0))
            self.screen.blit(self.tree_base_canvas, (0, 0))
            self.screen.blit(self.path_canvas, (0, 0))
            pygame.display.flip()
            clock.tick(5)  
        print("You won!" if won else "You lost!")
        
if __name__ == "__main__":
    pygame.init()
    game: Game = Game("./res/config.json")
    game.game_loop()