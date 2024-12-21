import random
import math
import json
import pygame
from itertools import cycle
from heapq import nlargest
from noise import snoise2
from gridElements import Block
from maze import Maze

class Map:
    def __init__(self, path: str, algorithm_visualisation: bool = False):        
        with open(path, "r") as file:
            data: dict = json.load(file)

        self.blocks_in_cell: int = data["blocks_in_cell"]
        self.map_width: int = data["maze_width_in_cells"] * self.blocks_in_cell
        self.map_height: int = data["maze_height_in_cells"] * self.blocks_in_cell
        self.block_size: int = data["block_size_px"]

        self.screen_width: int = data["screen_width_px"]
        self.screen_height: int = data["screen_height_px"]

        self.colors: dict = data.get("colors", {})

        self.locations: dict = data.get("locations", {})
        self.rivers: dict = data.get("rivers_data", {})

        self.block_width: int = self.screen_width // self.map_width
        self.block_height: int = self.screen_height // self.map_height

        self.noise_params: dict = data.get("noise_params", {})

        self.algorithm_visualisation: bool = algorithm_visualisation
        self.canvas: pygame.Surface = pygame.Surface((self.screen_width, self.screen_height))

        self.screen: pygame.Surface = None

        if algorithm_visualisation:
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            pygame.display.set_caption("Map creation algorithm visualisation")

        self.maze: Maze = Maze("./res/config.json", False, self.screen)

        self.location_circles: list[dict] = []
        self.map: list[list[Block]] = [[Block(x, y) for x in range(self.map_width)] for y in range(self.map_height)]
        self.lava_territory: set[Block] = set()
        self.forest_territory: set[Block] = set()
        
        self.generate_map()

    def generate_map(self) -> None:
        self.generate_circles()
        
        forest_circles: list[dict] = [circle for circle in self.location_circles if circle["location"] == "forest"]
        self.generate_forests(forest_circles)
        lava_circles: list[dict] = [circle for circle in self.location_circles if circle["location"] == "lava"]
        self.generate_lava(lava_circles)
        
        self.generate_hightmap()
        self.generate_rivers()

        self.location_circles = []
        self.implement_maze()

    def generate_circles(self) -> None:
        attempts_given: int = 100

        location_names: list[str] = list(self.locations.keys())
        location_counts: dict[str, int] = {loc: self.locations[loc]["count"] for loc in location_names}

        location_cycle = cycle(location_names)

        while any(location_counts[loc] > 0 for loc in location_names):
            location_name: str = next(location_cycle)
            
            if location_counts[location_name] == 0:
                continue

            for _ in range(attempts_given):
                location_data: dict = self.locations[location_name]
                r: int = random.randint(location_data["min_radius_in_blocks"], location_data["max_radius_in_blocks"])
                x: int = random.randint(r, self.map_width - r)
                y: int = random.randint(r, self.map_height - r)

                new_circle: dict = {
                    "location": location_name,
                    "position": (x, y),
                    "radius": r,
                }

                collide: bool = False
                for circle in self.location_circles:
                    if circle["location"] != new_circle["location"]:
                        if self.circles_collide(circle, new_circle):
                            collide = True
                            break

                if not collide:
                    self.location_circles.append(new_circle)
                    location_counts[location_name] -= 1
                    if self.algorithm_visualisation:
                        self.visualise(1)
                    break

    def circles_collide(self, c1: dict, c2: dict) -> bool:
        distance: float = math.sqrt((c1["position"][0] - c2["position"][0])**2 
                            + (c1["position"][1] - c2["position"][1])**2)
        
        return c1["radius"] + c2["radius"] + 1 >= distance
        
    def generate_forests(self, forest_circles: list[dict]) -> None:
        for forest in forest_circles:
            cx, cy = forest["position"]
            r: int = forest["radius"]

            for x in range(max(0, cx - r), min(self.map_width - 1, cx + r + 1)):
                for y in range(max(0, cy - r), min(self.map_width - 1, cy + r + 1)):
                    if (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2:
                        self.forest_territory.add(self.map[y][x])
        self.generate_trees()

    def generate_trees(self) -> None:
        used_blocks_coord: set[tuple[int, int]] = set()
        fill_pct: float = self.locations["forest"]["fill_pct"]

        trees_placed_algorithmicly: float = fill_pct * (3 / 4)
        while len(used_blocks_coord) < len(self.forest_territory) * trees_placed_algorithmicly:
            block: Block = random.choice(list(self.forest_territory))
            if (block.x, block.y) in used_blocks_coord:
                continue

            near_trees: list[Block] = self.get_near_trees(block)
            
            tree: Block = random.choice(near_trees)
            if self.tree_near(tree, used_blocks_coord):
                continue
            tree.trait["forest"] = True
            used_blocks_coord.add((tree.x, tree.y))

            tree = random.choice(near_trees)
            if self.tree_near(tree, used_blocks_coord):
                continue
            tree.trait["forest"] = True
            used_blocks_coord.add((tree.x, tree.y))

            if self.algorithm_visualisation:
                self.visualise(1) 

        while len(used_blocks_coord) < len(self.forest_territory) * fill_pct:
            block: Block = random.choice(list(self.forest_territory))
            block.trait["forest"] = True
            used_blocks_coord.add((block.x, block.y))
            if self.algorithm_visualisation:
                self.visualise(1) 

    def tree_near(self, tree: Block, trees_coord: set[tuple[int, int]]) -> bool:
        directions: list[list[int]] = [
            [-1, -1], [0, -1], [ 1, -1],
            [-1,  0],          [ 1,  0],
            [-1,  1], [0,  1], [ 1,  1],
        ]

        for d in directions:
            if (tree.x + d[0], tree.y + d[1]) in trees_coord:
                return True
        return False

    def get_near_trees(self, tree: Block) -> list[Block]:
        directions: list[list[int]] = [
            [-1, -1], [0, -1], [ 1, -1],
            [-1,  0],          [ 1,  0],
            [-1,  1], [0,  1], [ 1,  1],
        ]
        near_trees: list[Block] = []
        for d in directions:
            ntree: Block = self.get_tree_by_coord(tree.x + d[0], tree.y + d[1])
            if ntree:
                near_trees.append(ntree)
        return near_trees

    def get_tree_by_coord(self, x: int, y: int) -> Block:
        for tree in self.forest_territory:
            if x == tree.x and y == tree.y:
                return tree
        return None
    
    def generate_lava(self, lava_circle: list[dict]) -> None:
        for lava in lava_circle:
            cx, cy = lava["position"]
            r: int = lava["radius"]

            for x in range(max(0, cx - r), min(self.map_width - 1, cx + r + 1)):
                for y in range(max(0, cy - r), min(self.map_width - 1, cy + r + 1)):
                    if (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2:
                        self.lava_territory.add(self.map[y][x])
        self.create_lava_lakes()

    def create_lava_lakes(self) -> None:
        used_blocks: set[tuple[int, int]] = set()
        lakes: list[set[Block]] = []
        lava_fill_pct: float = self.locations["lava"]["fill_pct"]

        while len(used_blocks) < len(self.lava_territory) * lava_fill_pct:
            lake_start: Block = random.choice(list(self.lava_territory))
            if (lake_start.x, lake_start.y) in used_blocks or lake_start.get_traits() is not None:
                continue
            if self.other_lake_near(lake_start, lakes, 5):
                continue

            lava_lake_border: set[Block] = self.create_lava_lake_border(lake_start)
            lake: set[Block] = set()

            current_block: Block = random.choice(list(lava_lake_border))
            lake.add(current_block) 
            used_blocks.add((current_block.x, current_block.y))
            lava_lake_border.remove(current_block)

            while len(lake) < self.locations["lava"]["max_lake_size"]:
                new_block: Block = self.get_one_nearest(current_block, lava_lake_border)
                if new_block is None:
                    break
                if (new_block.x, new_block.y) in used_blocks:
                    break
                if self.other_lake_near(new_block, lakes, 4):
                    break

                lake.add(new_block)
                used_blocks.add((new_block.x, new_block.y))
                lava_lake_border.remove(new_block)
                current_block = new_block

            if len(lake) >= self.locations["lava"]["min_lake_size"]:
                for lava in lake:
                    lava.trait["lava"] = True  
                    if self.algorithm_visualisation:
                        self.visualise(1) 
    
    def other_lake_near(self, block: Block, lakes: list[set[Block]], min_dist: int) -> bool:
        dist: float = float('inf')
        for lake in lakes:
            for l in lake:
                new_dist: int = abs(block.x - l.x) + abs(block.y - l.y)
                if new_dist < dist:
                    dist = new_dist
        return dist <= min_dist

    def create_lava_lake_border(self, block: Block) -> set[Block]:
        lake: set[Block] = set(self.get_lava_neighbors(block))
        while len(lake) <= self.locations["lava"]["max_lake_size"] * 2:
            lake = lake | set(self.get_lava_neighbors(random.choice(list(lake))))
        lake.add(block)
        return set(lake)

    def get_lava_neighbors(self, block: Block) -> list[Block]:
        directions: list[list[int]] = [
            [-1, -1], [0, -1], [ 1, -1],
            [-1,  0],          [ 1,  0],
            [-1,  1], [0,  1], [ 1,  1],
        ]
        neighbors: list[Block] = []
        for d in directions:
            nblock: Block = self.get_lava_by_coord(block.x + d[0], block.y + d[1])
            if nblock:
                neighbors.append(nblock)
        return neighbors

    def get_lava_by_coord(self, x: int, y: int) -> Block:
        for lava in self.lava_territory:
            if x == lava.x and y == lava.y:
                return lava
        return None

    def get_one_nearest(self, block: Block, blocks: set[Block]) -> Block:
        nearest: list[Block] = []
        dist: float = float('inf')
        for b in blocks:
            new_dist: int = abs(block.x - b.x) + abs(block.y - b.y)
            if new_dist < dist:
                dist = new_dist
                nearest = [b]
            elif new_dist == dist:
                nearest.append(b)
        return random.choice(nearest) if nearest else None
    
    def generate_hightmap(self) -> None:
        seed: int = random.randint(0, 123456)
        for row in self.map:
            for block in row:
                noise_value: float = snoise2(
                    block.x * self.noise_params["scale"],
                    block.y * self.noise_params["scale"],
                    octaves = self.noise_params["octaves"],
                    persistence = self.noise_params["persistence"],
                    lacunarity = self.noise_params["lacunarity"],
                    base = seed
                )
                block.height = (noise_value + 1) / 2
            
            if self.algorithm_visualisation:
                self.visualise(1)

    def generate_rivers(self) -> None:
        margi_x: int = len(self.map[0]) // 10
        margi_y: int = len(self.map) // 10
        all_blocks: list[Block] = [block for row in self.map[margi_y:-margi_y] for block in row[margi_x:-margi_x]]
        top_blocks: list[Block] = self.select_river_starts(all_blocks, self.rivers["count"])

        for start_block in top_blocks:
            current: Block = start_block
            river_path: list[Block] = []

            while current:
                if len(river_path) >= self.rivers["max_length"]:
                    break
                if current.get_traits() is not None:
                    break 
                
                if current in self.lava_territory:
                    break

                current.trait["river"] = True
                river_path.append(current)

                if self.algorithm_visualisation:
                    self.visualise(1)

                neighbors: list[Block] = self.get_valid_river_neighbors(current, river_path)
                neighbors = [n for n in neighbors if n.get_traits() is None and n not in self.lava_territory]  
                if not neighbors:
                    break 

                next_block: Block = min(neighbors, key=lambda b: b.height)

                current = next_block
            if len(river_path) < self.rivers["min_length"]:
                for block in river_path:
                    block.trait["river"] = False
                    if self.algorithm_visualisation:
                        self.visualise(1)

    def select_river_starts(self, all_blocks: list[Block], num_rivers: int) -> list[Block]:
        sorted_blocks: list[Block] = nlargest(len(all_blocks), all_blocks, key=lambda b: b.height)
        selected_starts: list[Block] = []

        for block in sorted_blocks:
            if len(selected_starts) >= num_rivers:
                break

            too_close: bool = False
            for selected in selected_starts:
                distance: int = abs(block.x - selected.x) + abs(block.y - selected.y)
                if distance < self.rivers["min_distance"]:
                    too_close = True
                    break

            if not too_close and block not in self.lava_territory:
                selected_starts.append(block)

        return selected_starts
    
    def get_valid_river_neighbors(self, current: Block, river_path: list[Block]) -> list[Block]:
        neighbors: list[Block] = []
        for neighbor in self.get_river_neighbors(current):
            if neighbor.get_traits() is None and neighbor not in self.lava_territory:
                check_distance: int = 2
                counter: int = 0
                for block in river_path:
                    if abs(neighbor.x - block.x) + abs(neighbor.y - block.y) <= check_distance:
                        counter += 1
                if counter < 4:
                    neighbors.append(neighbor)
        return neighbors

    def get_river_neighbors(self, block: Block) -> list[Block]:
        directions: list[list[int]] = [
            [-1, 0], [1, 0], [0, -1], [0, 1]
        ]
        neighbors: list[Block] = []
        for d in directions:
            nblock: Block = self.get_river_by_coord(block.x + d[0], block.y + d[1])
            if nblock:
                neighbors.append(nblock)
        return neighbors

    def get_river_by_coord(self, x: int, y: int) -> Block:
        if x < 0 or x >= len(self.map[0]) or y < 0 or y >= len(self.map):
            return None
        return self.map[y][x]

    def implement_maze(self) -> None:
        maze_map: list[list[Block]] = self.maze.maze

        for my in range(len(maze_map)):
            for mx in range(len(maze_map[my])):
                cell_walls: dict = maze_map[my][mx].walls
                need_walls_top: bool = True if my == 0 else False
                need_walls_down: bool = True if my == len(maze_map)-1 else False
                
                need_walls_left: bool = True if mx == 0 else False
                need_walls_right: bool = True if mx == len(maze_map[my])-1 else False
                
                if cell_walls["top"]:
                    for x in range(self.blocks_in_cell):
                        if need_walls_top or self.map[my * self.blocks_in_cell][mx * self.blocks_in_cell + x].get_traits() is None:
                            self.map[my * self.blocks_in_cell][mx * self.blocks_in_cell + x].walls["top"] = True
                if cell_walls["down"]:
                    for x in range(self.blocks_in_cell):
                        if need_walls_down or self.map[(my + 1) * self.blocks_in_cell - 1][mx * self.blocks_in_cell + x].get_traits() is None:
                            self.map[(my + 1) * self.blocks_in_cell - 1][mx * self.blocks_in_cell + x].walls["down"] = True
                if cell_walls["right"]:
                    for y in range(self.blocks_in_cell):
                        if need_walls_right or self.map[my * self.blocks_in_cell + y][(mx + 1) * self.blocks_in_cell - 1].get_traits() is None:
                            self.map[my * self.blocks_in_cell + y][(mx + 1) * self.blocks_in_cell - 1].walls["right"] = True
                if cell_walls["left"]:
                    for y in range(self.blocks_in_cell):
                        if need_walls_left or self.map[my * self.blocks_in_cell + y][mx * self.blocks_in_cell].get_traits() is None:
                            self.map[my * self.blocks_in_cell + y][mx * self.blocks_in_cell].walls["left"] = True
                if self.algorithm_visualisation:
                        self.visualise(1)

    def check_pygame_exit(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
        return False
    
    def visualise(self, delay: int) -> None:
        self.canvas.fill(pygame.Color(self.colors["maze_path"]))
        self.update_canvas()
        self.check_pygame_exit()
        self.screen.fill(pygame.Color(self.colors["maze_path"]))
        self.screen.blit(self.canvas, (0, 0)) 
        pygame.display.flip()
        pygame.time.delay(delay)

    def update_canvas(self, n_canvas: pygame.Surface = None) -> None:
        canvas: pygame.Surface = self.canvas if not n_canvas else n_canvas
        wall_color: str = self.colors["maze_walls"]

        for y in range(self.map_height):
            for x in range(self.map_width):
                
                block: Block = self.map[y][x]  # Get the block at position (x, y)
                
                active_traits: list[str] = block.get_traits()  
                color: tuple = self.generate_height_color(block)
                if active_traits:
                    for trait in active_traits:
                        color = self.colors[trait]
                pygame.draw.rect(self.canvas, color, (x * self.block_size, y * self.block_size, self.block_size, self.block_size))

                if block.walls["top"]:
                    pygame.draw.line(canvas, pygame.Color(wall_color), (x * self.block_size, y * self.block_size), ((x + 1) * self.block_size - 1, y * self.block_size), 1)
                if block.walls["down"]:
                    pygame.draw.line(canvas, pygame.Color(wall_color), (x * self.block_size, (y + 1) * self.block_size - 1), ((x + 1) * self.block_size - 1, (y + 1) * self.block_size - 1), 1)
                if block.walls["left"]:
                    pygame.draw.line(canvas, pygame.Color(wall_color), (x * self.block_size, y * self.block_size), (x * self.block_size, (y + 1) * self.block_size - 1), 1)
                if block.walls["right"]:
                    pygame.draw.line(canvas, pygame.Color(wall_color), ((x + 1) * self.block_size - 1, y * self.block_size), ((x + 1) * self.block_size - 1, (y + 1) * self.block_size - 1), 1)


        for circle in self.location_circles:
            location_name: str = circle["location"]
            color: tuple = self.colors[location_name]  # Default to white if no color found
            
            center_x: int = circle["position"][0] * self.block_size  # Convert to pixel-based position
            center_y: int = circle["position"][1] * self.block_size  # Convert to pixel-based position
            r: int = circle["radius"] * self.block_size
            pygame.draw.circle(self.canvas, color, (center_x, center_y), r, width=2)

    def generate_height_color(self, block: Block) -> tuple:
        color: tuple = self.colors["terrain"]
        adjusted_color: tuple = tuple(c * block.height for c in color)
        return adjusted_color
    
    def show_loop(self) -> None:
        self.visualise(100)

        while True:
            if self.check_pygame_exit(): return
            pygame.time.delay(100)

    def save_as_image(self, name: str) -> None:
        self.update_canvas()
        pygame.image.save(self.canvas, f"./res/{name}.png")

if __name__ == "__main__":
    m = Map("./res/config.json", True)
    m.show_loop()