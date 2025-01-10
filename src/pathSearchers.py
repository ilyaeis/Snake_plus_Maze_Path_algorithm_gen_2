from snake import Snake, SnakeBodyBlock, Apple
from gridElements import Block, Node
from collections import deque

class BFS:
    def __init__(self, map: list[list[Block]]):
        self.map: list[list[Block]] = map
        self.bounds: tuple[int, int] = (len(self.map[0]), len(self.map))
        self.path: list[tuple[int, int]] = []
        self.longest_path: list[tuple[int, int]] = []
        self.snake_values: set[tuple[int, int]] = set()
        self.target_values: set[tuple[int, int]] = set()
        
    def get_snake_values(self, snake: Snake):
        for block in snake.body:
            self.snake_values.add((block.x, block.y))
            
    def get_target_values(self, targets: list[any]):
        for block in targets:
            self.target_values.add((block.x, block.y))
                
    def check_bounds(self, position: tuple[int, int]) -> bool:
        return (0 <= position[0] < self.bounds[0] and
                0 <= position[1] < self.bounds[1])
        
    def check_block_collision(self, position: tuple[int, int])  -> bool: 
        return (position not in self.snake_values and
                (not self.map[position[1]][position[0]].get_traits() or
                 self.map[position[1]][position[0]].get_traits() == ["river"]))
         
    def check_wall_collision(self, direction: tuple[int, int], current_position: tuple[int, int], next_position: tuple[int, int])  -> bool: 
        current_pos_walls: list[str] = self.map[current_position[1]][current_position[0]].get_walls()
        next_pos_walls: list[str] = self.map[next_position[1]][next_position[0]].get_walls() 

        current_pos_walls = current_pos_walls if current_pos_walls else []
        next_pos_walls = next_pos_walls if next_pos_walls else []
        if current_pos_walls or next_pos_walls:
            if direction[0] == 1 and ("right" in current_pos_walls or "left" in next_pos_walls):
                return False
            elif direction[0] == -1 and ("left" in current_pos_walls or "right" in next_pos_walls):
                return False
            
            if direction[1] == 1 and ("down" in current_pos_walls or "top" in next_pos_walls):
                return False
            elif direction[1] == -1 and ("top" in current_pos_walls or "down" in next_pos_walls):
                return False
        
        return True
        
    def create_path(self, snake: Snake, targets: list[any]):
        self.path = []
        self.longest_path = []
        self.get_snake_values(snake)
        self.get_target_values(targets)
        
        start: tuple[int, int] = (snake.body[0].x, snake.body[0].y)
        directions: list[tuple[int, int]] = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        # Initialize BFS queue with Node
        start_node = Node(start)
        queue = deque([start_node])
        visited: set[tuple[int, int]] = {start}

        # Keep track of the farthest node and its depth
        farthest_node = start_node
        max_depth = 0

        while queue:
            current_node: Node = queue.popleft()
            current_position: tuple[int, int] = current_node.position
            depth = current_node.depth  
            
            if depth > max_depth:
                farthest_node = current_node
                max_depth = depth

            if current_position in self.target_values:
                while current_node is not None:
                    self.path.append(current_node.position)
                    current_node = current_node.parent
                self.path.reverse()
                return

            for dx, dy in directions:
                neighbor_position = (current_position[0] + dx, current_position[1] + dy)
                direction = (dx, dy)
                if (
                    self.check_bounds(neighbor_position) and
                    neighbor_position not in visited and
                    self.check_block_collision(neighbor_position) and
                    self.check_wall_collision(direction, current_position, neighbor_position)
                ):
                    neighbor_node = Node(neighbor_position, current_node, depth=depth + 1)
                    queue.append(neighbor_node)
                    visited.add(neighbor_position)

        # If no path to an apple is found, reconstruct the longest path
        while farthest_node is not None:
            self.longest_path.append(farthest_node.position)
            farthest_node = farthest_node.parent
        self.longest_path.reverse()