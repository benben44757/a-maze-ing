import sys
sys.setrecursionlimit(10000)

import random
import os

from mazegen.config_parser import ConfigParser
from mazegen.generator import MazeGenerator
from mazegen.solver import MazeSolver

USE_ASCII_CHARS = False 

class TerminalDisplay:
    def __init__(self, generator, config):
        self.generator = generator
        self.config = config
        self.width = config.width
        self.height = config.height
        
    def render(self, solution_path=None):
        if USE_ASCII_CHARS:
            W_BLK = "##"
            P_BLK = "  "
            S_BLK = ".."
            E_BLK = "SS"
            X_BLK = "EE"
        else:
            RESET = "\033[0m"
            W_BLK = f"\033[47m  {RESET}"
            P_BLK = f"\033[40m  {RESET}"
            S_BLK = f"\033[42m  {RESET}"
            E_BLK = f"\033[44m  {RESET}"
            X_BLK = f"\033[41m  {RESET}"

        os.system('cls' if os.name == 'nt' else 'clear')

        path_set = set(solution_path) if solution_path else set()

        print(f"Maze: {self.width}x{self.height} | Seed: {self.generator.seed}")
        print("Controls: [Enter] Regenerate | [S] Toggle Solution | [Q] Quit\n")

        for y in range(self.height):
            top_line = ""
            mid_line = ""
            bot_line = ""

            for x in range(self.width):
                cell = self.generator.maze[y][x]
                
                if (x, y) == self.config.entry:
                    floor = E_BLK
                elif (x, y) == self.config.exit:
                    floor = X_BLK
                elif (x, y) in path_set:
                    floor = S_BLK
                else:
                    floor = P_BLK

                wall_n = (cell.walls & 1) != 0
                wall_e = (cell.walls & 2) != 0
                wall_s = (cell.walls & 4) != 0
                wall_w = (cell.walls & 8) != 0

                center = floor

                n_char = W_BLK if wall_n else floor
                s_char = W_BLK if wall_s else floor
                e_char = W_BLK if wall_e else floor
                w_char = W_BLK if wall_w else floor
                
                corner = W_BLK

                top_line += f"{corner}{n_char}{corner}"
                mid_line += f"{w_char}{center}{e_char}"
                bot_line += f"{corner}{s_char}{corner}"

            print(top_line)
            print(mid_line)
            print(bot_line)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return

    try:
        config = ConfigParser(sys.argv[1])
        config.parse()
    except Exception as e:
        print(f"Error loading config: {e}")
        return

    show_path = False 

    while True:
        seed = config.seed if config.seed is not None else random.randint(0, 999999)
        gen = MazeGenerator(config.width, config.height, seed)
        gen.generate()

        solver = MazeSolver(gen.maze, config.entry, config.exit)
        directions = solver.solve() 

        with open(config.output_file, "w") as f:
            f.write(gen.to_hex())
            f.write("\n")
            f.write(f"{config.entry[0]},{config.entry[1]}\n")
            f.write(f"{config.exit[0]},{config.exit[1]}\n")
            f.write("".join(directions) + "\n")

        path_coords = []
        if show_path:
            cx, cy = config.entry
            path_coords.append((cx, cy))
            for move in directions:
                if move == 'N': cy -= 1
                elif move == 'S': cy += 1
                elif move == 'E': cx += 1
                elif move == 'W': cx -= 1
                path_coords.append((cx, cy))
        
        display = TerminalDisplay(gen, config)
        display.render(solution_path=path_coords)

        if len(directions) == 0:
            print("\nWARNING: No path found! The maze might be fully closed.")
        
        cmd = input("Command > ").strip().lower()
        if cmd == 'q':
            break
        elif cmd == 's':
            show_path = not show_path
            config.seed = seed
        else:
            config.seed = None
            show_path = False

if __name__ == "__main__":
    main()