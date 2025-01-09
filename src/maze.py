import json
import random
import pygame
import sys
from gridElements import Cell

class Maze:
    def __init__(self, path: str, algorithm_visualisation: bool = False, screen: pygame.Surface = None) -> None:
        with open(path, "r") as file:
            data: dict = json.load(file)

        self.maze_width: int = data["maze_width_in_cells"]
        self.maze_height: int = data["maze_height_in_cells"]

        self.screen_width: int = data["screen_width_px"]
        self.screen_height: int = data["screen_height_px"]

        self.colors: dict = data.get("colors", {})

        self.maze: list[list[Cell]] = []

        self.start: Cell = Cell(0, 0)
        self.end: Cell = Cell(self.maze_width - 1, self.maze_height - 1)

        self.algorithm_visualisation: bool = algorithm_visualisation
        self.canvas: pygame.Surface = pygame.Surface((self.screen_width, self.screen_height)) 

        if algorithm_visualisation:
            self.screen: pygame.Surface = pygame.display.set_mode((self.screen_width, self.screen_height)) if not screen else screen
            pygame.display.set_caption("Maze creation algorithm visualisation")

        self.generate_maze()

    def remove_walls(self, current_cell: Cell, next_cell: Cell) -> None:
        dx: int = current_cell.x - next_cell.x
        dy: int = current_cell.y - next_cell.y

        if dx == -1:
            current_cell.walls["right"] = False
            next_cell.walls["left"] = False
        elif dx == 1:
            current_cell.walls["left"] = False
            next_cell.walls["right"] = False

        if dy == -1:
            current_cell.walls["down"] = False
            next_cell.walls["top"] = False
        elif dy == 1:
            current_cell.walls["top"] = False
            next_cell.walls["down"] = False

    def generate_maze(self) -> None:
        for y in range(self.maze_height):
            self.maze.append([])
            for x in range(self.maze_width):
                self.maze[y].append(Cell(x, y))
                if self.algorithm_visualisation:
                    self.visualise(0, self.maze[y][x])

        current_cell: Cell = self.maze[self.start.y][self.start.x]
        stack: list[Cell] = []
        counter: int = 1

        while counter < self.maze_width * self.maze_height:
            current_cell.visited = True
            neighbors: list[Cell] = current_cell.get_neighbors(self.maze)
            
            if neighbors:
                random.shuffle(neighbors)
                next_cell: Cell = random.choice(neighbors)
                counter += 1
                stack.append(next_cell)
                self.remove_walls(current_cell, next_cell)
                current_cell = next_cell

                if self.algorithm_visualisation:
                    self.visualise(100, current_cell)
            else:
                current_cell = stack.pop(1 if len(stack) > 0 else 0)
                if self.algorithm_visualisation:
                    self.visualise(50, current_cell)

        
    def check_pygame_exit(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
        return False

    def update_canvas(self, current_cell: Cell = None, n_canvas: pygame.Surface = None) -> None:
        canvas: pygame.Surface = self.canvas if not n_canvas else n_canvas
        wall_color: str = self.colors["maze_walls"]

        cell_width: float = self.screen_width / self.maze_width
        cell_height: float = self.screen_height / self.maze_height   

        for y, row in enumerate(self.maze):  
            for x, cell in enumerate(row): 
                if (x, y) == (self.start.x, self.start.y):
                    pygame.draw.rect(
                        canvas,
                        (100, 100, 255), 
                        (x * cell_width, y * cell_height, cell_width, cell_height)
                    )

                if (x, y) == (self.end.x, self.end.y):
                    pygame.draw.rect(
                        canvas,
                        (255, 100, 100),  
                        (x * cell_width, y * cell_height, cell_width, cell_height)
                    )

                if current_cell and (x, y) == (current_cell.x, current_cell.y):
                    pygame.draw.rect(
                        canvas,
                        (200, 255, 200, 100),  
                        (x * cell_width, y * cell_height, cell_width, cell_height)
                    )

                if cell.walls["top"]:
                    pygame.draw.line(canvas, pygame.Color(wall_color), (x * cell_width, y * cell_height), ((x + 1) * cell_width - 1, y * cell_height), 1)
                if cell.walls["down"]:
                    pygame.draw.line(canvas, pygame.Color(wall_color), (x * cell_width, (y + 1) * cell_height - 1), ((x + 1) * cell_width - 1, (y + 1) * cell_height - 1), 1)
                if cell.walls["left"]:
                    pygame.draw.line(canvas, pygame.Color(wall_color), (x * cell_width, y * cell_height), (x * cell_width, (y + 1) * cell_height - 1), 1)
                if cell.walls["right"]:
                    pygame.draw.line(canvas, pygame.Color(wall_color), ((x + 1) * cell_width - 1, y * cell_height), ((x + 1) * cell_width - 1, (y + 1) * cell_height - 1), 1)

    def visualise(self, delay: int, current_cell: Cell = None) -> None:
        self.canvas.fill(pygame.Color(self.colors["maze_path"]))
        self.update_canvas(current_cell)
        if self.check_pygame_exit():
            sys.exit()
        self.screen.fill(pygame.Color(self.colors["maze_path"]))
        self.screen.blit(self.canvas, (0, 0)) 
        pygame.display.flip()
        pygame.time.delay(delay)

    def show_loop(self) -> None:
        self.visualise(100)

        while True:
            if self.check_pygame_exit():
                return
            pygame.time.delay(100)

    def save_as_image(self, name: str) -> None:
        self.update_canvas()
        pygame.image.save(self.canvas, f"./res/{name}.png")

if __name__ == "__main__":
    pygame.init()
    m: Maze = Maze("./res/config.json", True)
    m.show_loop()
    pygame.quit()
