# Goal
This project aims to create an complex version of the classic Snake game. The idea is to combine traditional game play with dynamic maze elements, unique features, and eventually, an autonomous controlled snake.

## Key Features 
1. Maze Integration
    - The snake will navigate through a maze with walls and special cells.
2. Special Maze Cells
    - Forest Cell: Have tree in it, which are dangerous for snake and under the tree crown nothing is seen.
    - Teleport Cell: Moves the snake to a random location in the maze.

# Structure
### 📂res
##### config.json
Contains all the data for the project.
### 📂src
#### Cell.py
Contains the `Cell` class, which is used for maze creation with the DFS Recursive Backtracking algorithm.
- **Functions** 
	- `Cell.__init__(self, x: int, y: int)`
	- `Cell.get_neighbors(self, maze: List[List['Cell']]) -> List['Cell']`
	- `Cell.to_string(self) -> str`
- **Variables**
	- `self.walls = { "right": True, "left": True, "top": True, "down": True }`
	- `self.x: int, self.y: int`
	- `self.visited: bool`
#### Maze.py
Contains the `Maze` class for maze creation, its algorithm visualisation, and further use in the program.
- **Functions** 
	- `Maze.__init__(self, path: str, algorithm_visualisation: bool = False)`
	- `Maze.remove_walls(self, current_cell: Cell, next_cell: Cell)`
	- `Maze.generate_maze(self)`
	- `Maze.check_pygame_event(self)`
	- `Maze.update_canvas(self, current_cell: Cell)`
	- `Maze.update_screen(self, delay: int, current_cell: Cell)`
	- `Maze.visualisation(self)`
	- `Maze.__str__(self)`
- **Variables**
	- `self.maze_width: int, self.maze_height: int`
	- `self.screen_width: int, self.screen_height: int`
	- `self.blocks_in_cell: int`
	- `self.maze: List[List['Cell']]`
	- `self.start: Cell, self.end: Cell`