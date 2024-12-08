from typing import List

class Cell:
    def __init__(self, x: int, y: int):
        self.walls = {
            "right": True,
            "left": True,
            "top": True,
            "down": True
        }
        self.x, self.y = x, y
        self.visited = False
        
    def get_neighbors(self, maze: List[List['Cell']]) -> List['Cell']:
        neighbors = []

        if self.x > 0 and not maze[self.y][self.x - 1].visited:
            neighbors.append(maze[self.y][self.x - 1])
        if self.x < len(maze[self.y]) - 1 and not maze[self.y][self.x + 1].visited:
            neighbors.append(maze[self.y][self.x + 1])
        if self.y > 0 and not maze[self.y - 1][self.x].visited:
            neighbors.append(maze[self.y - 1][self.x])
        if self.y < len(maze) - 1 and not maze[self.y + 1][self.x].visited:
            neighbors.append(maze[self.y + 1][self.x])

        return neighbors
    
    def to_string(self) -> str:
        return f"(x: {self.x}, y: {self.y}, {self.walls})"