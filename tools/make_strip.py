"""Make docs/pipeline.png: a 3-stage strip (maze, terrain, BFS path).

Runs the game code headless (SDL "dummy" driver) and grabs the screen.
The game code stays unchanged.

From the repo root:
    uv run --python 3.12 --with pygame --with noise --with pillow tools/make_strip.py
"""
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "src")

import pygame  # noqa: E402
from PIL import Image  # noqa: E402

CONFIG = "./res/config.json"
SEED = 7
SIZE = 400  # width of each stage in the strip


class Enough(Exception):
    pass


def to_image(surface):
    image = Image.frombytes("RGB", surface.get_size(), pygame.image.tobytes(surface, "RGB"))
    return image.resize((SIZE, SIZE), Image.LANCZOS)


def grab_flip(stop_at):
    """Patch pygame.display.flip to keep the screen at flip number `stop_at`."""
    shots, count = [], [0]
    real = pygame.display.flip

    def flip():
        real()
        count[0] += 1
        if count[0] == stop_at:
            shots.append(to_image(pygame.display.get_surface()))
            raise Enough
    pygame.display.flip = flip
    return shots, real


def main():
    pygame.init()
    pygame.time.Clock = lambda: type("C", (), {"tick": lambda *_: 0})()
    pygame.time.delay = lambda *_: None
    random.seed(SEED)
    from maze import Maze
    from map import Map
    from game import Game

    # Stage 1: maze generation, stopped part-way (after the 25 start flips, about 25 steps)
    shots, real = grab_flip(50)
    try:
        Maze(CONFIG, True)
    except Enough:
        pass
    pygame.display.flip = real
    stage1 = shots[0]

    # Stage 2: the whole map (terrain, rivers, lava, forests, maze walls)
    m = Map(CONFIG)
    side = m.map_width * m.block_size
    m.canvas = pygame.Surface((side, m.map_height * m.block_size))
    m.canvas.fill(pygame.Color(m.colors["maze_path"]))
    m.update_canvas()
    stage2 = to_image(m.canvas)

    # Stage 3: the game view with the BFS path drawn in red
    shots, real = grab_flip(1)
    game = Game(CONFIG)
    try:
        game.game_loop()
    except Enough:
        pass
    pygame.display.flip = real
    stage3 = shots[0]

    strip = Image.new("RGB", (SIZE * 3 + 20, SIZE), (30, 30, 30))
    for i, img in enumerate((stage1, stage2, stage3)):
        strip.paste(img, (i * (SIZE + 10), 0))
    os.makedirs("docs", exist_ok=True)
    strip.quantize(colors=128).save("docs/pipeline.png", optimize=True)
    print("docs/pipeline.png", os.path.getsize("docs/pipeline.png"), "bytes")


if __name__ == "__main__":
    main()
