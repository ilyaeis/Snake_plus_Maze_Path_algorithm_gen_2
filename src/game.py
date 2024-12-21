import json
import pygame
import math

from snake import Snake, Apple, SnakeBodyBlock
from map import Map
from gridElements import Block 

class Game:
    def __init__(self, path: str):
        with open(path, "r") as file:
            data: dict = json.load(file)

        blocks_in_cell: int = data["blocks_in_cell"]
        self.map_width: int = data["maze_width_in_cells"] * blocks_in_cell
        self.map_height: int = data["maze_height_in_cells"] * blocks_in_cell

        self.screen_width: int = data["screen_width_px"]
        self.screen_height: int = data["screen_height_px"]

        self.block_size: int = data["block_size_px"]
        self.tree_size: float = data["tree_size"]

        self.colors: dict = data.get("colors", {})
        
        maps_obj: Map = Map(path)
        self.map: list[list[Block]] = maps_obj.map
        start_location: tuple[int, int] = self.find_start_location()
        
        if start_location:
            self.snake: Snake = Snake(path, start_location)
        else:
            print("No location to start, please re-start! :)")
            return
        
        self.screen: pygame.Surface = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        self.background_canvas: pygame.Surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.maze_canvas: pygame.Surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.snake_canvas: pygame.Surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.tree_crown_canvas: pygame.Surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.tree_base_canvas: pygame.Surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        
    def find_start_location(self) -> tuple[int, int]:
        for x in range(self.map_width // 4, 3 * self.map_width // 4):
            for y in range(self.map_height // 4, 3 * self.map_height // 4):
                if not self.neighbours_has_traits(x, y) and self.map[y][x].get_walls() is None:
                    return (x, y)
        return None

    def neighbours_has_traits(self, x: int, y: int) -> bool:
        directions: list[list[int]] = [
            [-1, -1], [0, -1], [ 1, -1],
            [-1,  0],          [ 1,  0],
            [-1,  1], [0,  1], [ 1,  1],
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
        self.maze_canvas.fill((0, 0, 0, 0))
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

                active_traits: list[str] = block.get_traits()  
                color: tuple = self.generate_height_color(block)
                if active_traits:
                    if "forest" in active_traits:
                        crown_size: float = self.block_size * self.tree_size
                        margin_px: float = 0.5 * (1 - self.tree_size) * self.block_size
                        pygame.draw.ellipse(self.tree_crown_canvas, self.colors["tree_crown"], (bx + margin_px, by + margin_px, crown_size, crown_size))
                        pygame.draw.rect(self.tree_base_canvas, self.colors["forest"], (bx + 1, by + 1, self.block_size - 2, self.block_size - 2))
                    for trait in active_traits:
                        color = self.colors[trait]
                    pygame.draw.rect(self.background_canvas, color, (bx, by, self.block_size, self.block_size))
                else:
                    pygame.draw.rect(self.background_canvas, color, (bx + 1, by + 1, self.block_size - 2, self.block_size - 2))

                if block.walls["top"]:
                    pygame.draw.line(self.maze_canvas, pygame.Color(wall_color), (bx, by), (bx + self.block_size, by), 1)
                if block.walls["down"]:
                    pygame.draw.line(self.maze_canvas, pygame.Color(wall_color), (bx, by + self.block_size ), (bx + self.block_size, by + self.block_size), 1)
                if block.walls["left"]:
                    pygame.draw.line(self.maze_canvas, pygame.Color(wall_color), (bx, by), (bx, by + self.block_size), 1)
                if block.walls["right"]:
                    pygame.draw.line(self.maze_canvas, pygame.Color(wall_color), (bx + self.block_size, by), (bx + self.block_size, by + self.block_size), 1)

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

    def game_loop(self) -> None:
        clock: pygame.time.Clock = pygame.time.Clock()
        running: bool = True
        
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
            
            self.snake.check_snake_collision(snake_block, next_block)
            self.snake.move()

            self.screen.fill(pygame.Color(self.colors["maze_path"]))
            self.update_world_canvas()
            self.update_snake_canvas()
            self.screen.blit(self.background_canvas, (0,0))
            self.screen.blit(self.snake_canvas, (0,0))
            self.screen.blit(self.maze_canvas, (0,0))
            self.screen.blit(self.tree_crown_canvas, (0,0))
            self.screen.blit(self.tree_base_canvas, (0,0))
            pygame.display.flip()
            clock.tick(5)  

if __name__ == "__main__":
    pygame.init()
    game: Game = Game("./res/config.json")
    game.game_loop()