import json
import random
import pygame
import sys
from Cell import Cell

class Maze:
    def __init__(self, path: str, algorithm_visualisation: bool = False):
        with open(path, "r") as file:
            data = json.load(file)

        self.maze_width = data["maze_width_in_blocks"]
        self.maze_height = data["maze_height_in_blocks"]

        self.screen_width = data["screen_width_px"]
        self.screen_height = data["screen_height_px"]

        self.blocks_in_cell = data["blocks_in_cell"]
        self.maze = []

        self.start = Cell(0, 0)
        self.end = Cell(self.maze_width - 1, self.maze_height - 1)

        if algorithm_visualisation:
            self.visualisation()
        else:
            self.generate_maze()

    def remove_walls(self, current_cell: Cell, next_cell: Cell):
        dx = current_cell.x - next_cell.x
        dy = current_cell.y - next_cell.y

        if (dx == -1):
            current_cell.walls["right"] = False
            next_cell.walls["left"] = False
        elif (dx == 1):
            current_cell.walls["left"] = False
            next_cell.walls["right"] = False

        if (dy == -1):
            current_cell.walls["down"] = False
            next_cell.walls["top"] = False
        elif (dy == 1):
            current_cell.walls["top"] = False
            next_cell.walls["down"] = False

    def generate_maze(self):
        self.maze = [[Cell(x, y) for x in range(self.maze_width)] for y in range(self.maze_height)]
        current_cell = self.maze[self.start.y][self.start.x]

        stack = []
        counter = 1

        while counter < self.maze_width * self.maze_height:
            current_cell.visited = True
            neighbors = current_cell.get_neighbors(self.maze)
            
            if neighbors:
                next_cell = random.choice(neighbors)
                counter += 1
                stack.append(next_cell)
                self.remove_walls(current_cell, next_cell)

                current_cell = next_cell
            else:
                current_cell = stack.pop()
    
    def check_pygame_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

    def update_canvas(self, current_cell: Cell):
        self.canvas.fill(pygame.Color("black"))
        cell_width = self.screen_width / self.maze_width
        cell_height = self.screen_height / self.maze_height   

        for y, row in enumerate(self.maze):  
            for x, cell in enumerate(row): 

                if cell.walls["top"]:
                    pygame.draw.line(self.canvas, pygame.Color("white"), (x * cell_width, y * cell_height), ((x + 1) * cell_width, y * cell_height), 1)
                if cell.walls["down"]:
                    pygame.draw.line(self.canvas, pygame.Color("white"), (x * cell_width, (y + 1) * cell_height), ((x + 1) * cell_width, (y + 1) * cell_height), 1)
                if cell.walls["left"]:
                    pygame.draw.line(self.canvas, pygame.Color("white"), (x * cell_width, y * cell_height), (x * cell_width, (y + 1) * cell_height), 1)
                if cell.walls["right"]:
                    pygame.draw.line(self.canvas, pygame.Color("white"), ((x + 1) * cell_width, y * cell_height), ((x + 1) * cell_width, (y + 1) * cell_height), 1)

                if (x, y) == (self.start.x, self.start.y):
                    pygame.draw.rect(
                        self.canvas,
                        (100, 100, 255), 
                        (x * cell_width + 5, y * cell_height + 5, cell_width - 10, cell_height - 10)
                    )

                if (x, y) == (self.end.x, self.end.y):
                    pygame.draw.rect(
                        self.canvas,
                        (255, 100, 100),  
                        (x * cell_width + 5, y * cell_height + 5, cell_width - 10, cell_height - 10)
                    )

                if (x, y) == (current_cell.x, current_cell.y):
                    pygame.draw.rect(
                        self.canvas,
                        (200, 255, 200, 100),  
                        (x * cell_width, y * cell_height, cell_width, cell_height)
                    )

    def update_screen(self, delay: int, current_cell: Cell):
        self.update_canvas(current_cell)
        self.check_pygame_event()
        self.screen.fill(pygame.Color("black"))
        self.screen.blit(self.canvas, (0, 0)) 
        pygame.display.flip()
        pygame.time.delay(delay)
        
    def visualisation(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("DFS Recursive Backtracking algorithm visualisation")

        self.canvas = pygame.Surface((self.screen_width, self.screen_height))

        # generate maze cells
        for y in range(self.maze_height):
            self.maze.append([])
            for x in range(self.maze_width):
                self.maze[y].append(Cell(x, y))
                self.update_screen(10, self.maze[y][x])

        # generate maze path
        current_cell = self.maze[self.start.y][self.start.x]

        stack = []
        counter = 1

        while counter < self.maze_width * self.maze_height:
            current_cell.visited = True
            neighbors = current_cell.get_neighbors(self.maze)
            
            if neighbors:
                next_cell = random.choice(neighbors)
                counter += 1
                stack.append(next_cell)
                self.remove_walls(current_cell, next_cell)
                current_cell = next_cell

                self.update_screen(100, current_cell)
            else:
                current_cell = stack.pop()
                self.update_screen(50, current_cell)

        pygame.quit()

    def __str__(self):
        maze_string= ""
        for row in self.maze:
            row_string = "".join([cell.to_string() for cell in row]) 
            maze_string += row_string + "\n"
        return maze_string

if __name__ == "__main__":
    m = Maze("./res/config.json", True)
    print(m)


