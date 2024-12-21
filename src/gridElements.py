class Cell:
    def __init__(self, x: int, y: int):
        self.walls: dict[str, bool] = {
            "right": True,
            "left": True,
            "top": True,
            "down": True
        }
        self.x: int
        self.y: int
        self.x, self.y = x, y
        self.visited: bool = False
        
    def get_neighbors(self, maze: list[list['Cell']]) -> list['Cell']:
        neighbors: list['Cell'] = []

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
    
class Block:
    def __init__(self, x: int, y: int):
        self.walls: dict[str, bool] = {
            "right": False,
            "left": False,
            "top": False,
            "down": False
        }
        self.trait: dict[str, bool] = {
            "forest": False,
            "lava": False,
            "river": False
        }
        self.x: int = x
        self.y: int = y
        self.height: float = 0

    def reset_walls(self) -> None:
        self.walls = {
            "right": False,
            "left": False,
            "top": False,
            "down": False
        }   
         
    def get_traits(self) -> list[str]:
        return [key for key, value in self.trait.items() if value] or None
    
    def get_walls(self) -> list[str]:
        return [key for key, value in self.walls.items() if value] or None

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"
    
    def __repr__(self) -> str:
        return f"({self.x}, {self.y}, {self.get_traits()}, {self.get_walls()})"
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Block):
            return self.x == other.x and self.y == other.y
        return False

    def __hash__(self) -> int:
        return hash((self.x, self.y))
