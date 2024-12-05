import tkinter as tk
import random
import numpy as np
from config import *
import sys
import keyboard as kb
from time import time #! Debugging time complexity for the implementation
import neat
from neat.parallel import ParallelEvaluator
import multiprocessing

class Game(tk.Frame):
    def __init__(self, INIT_HEADLESS=None, INIT_TRAINING=None):
        self.HEADLESS = HEADLESS if INIT_HEADLESS is None else INIT_HEADLESS
        self.TRAINING = TRAINING if INIT_TRAINING is None else INIT_TRAINING
        
        #tk.Frame.__init__(self)
        #self.HEADLESS = HEADLESS
        
        if self.HEADLESS:
            self.start_game()
            if not TRAINING:
                while True:
                    self.on_arrow_key()
                
        else:
            tk.Frame.__init__(self)
            self.grid()
            self.master.title('Gaming Gamer Gaming Games')

            self.main_grid = tk.Frame(
                self, bg=GRID_COLOR, bd=3, width=600, height=600)
            self.main_grid.grid(pady=(80, 0))
            self.Init_GUI(self.HEADLESS)

            self.master.bind("<Left>", self.left)
            self.master.bind("<Right>", self.right)
            self.master.bind("<Up>", self.up)
            self.master.bind("<Down>", self.down)
            self.start_game()

            self.mainloop()
        
    def Init_GUI(self, Headless) -> None:
        if not Headless:
            self.cells = []
            for i in range(4):
                row = []
                for j in range(4):
                    cell_frame = tk.Frame(
                        self.main_grid,
                        bg=EMPTY_COLOR,
                        width=120,
                        height=120)
                    cell_frame.grid(row=i, column=j, padx=5, pady=5)
                    cell_number = tk.Label(self.main_grid, bg=EMPTY_COLOR)
                    cell_number.grid(row=i, column=j)
                    cell_data = {"frame": cell_frame, "number": cell_number}
                    row.append(cell_data)
                self.cells.append(row)

            # make score header
            score_frame = tk.Frame(self)
            score_frame.place(relx=0.5, y=40, anchor="center")
            tk.Label(
                score_frame,
                text="Score",
                font=SCORE_LABEL_FONT).grid(
                row=0)
            self.score_label = tk.Label(score_frame, text="0", font=SCORE_FONT)
            self.score_label.grid(row=1)
            
#! _________________________ Keyboard Interaction for Headless Usage _________________________
#? This shit gets removed when we are actually training DP model. 
    def on_arrow_key(self):
        key_event = kb.read_event()
        if key_event.event_type == kb.KEY_DOWN:
            if key_event.name == 'up':
                self.up(None)
            elif key_event.name == 'down': 
                self.down(None)
            elif key_event.name == 'left':
                self.left(None)
            elif key_event.name == 'right':
                self.right(None)
            
#! _________________________ INIT Game _________________________
    """
        Inits the 4x4 Matrix full of 0s and randomly places 2 random cells with either a 2 or 4
    """
    def start_game(self) -> None:
        # create 2D 4x4 matrix of zeroes
        self.matrix = np.zeros((4, 4), dtype=int)

        # fill 2 random cells with 2s
        for _ in range(2):
            row, col = np.random.randint(0, 4, size=2)
            while self.matrix[row, col] != 0:
                row, col = np.random.randint(0, 4, size=2)
            self.matrix[row, col] = np.random.choice([2, 4])

        if not self.HEADLESS:
            for row in range(4):
                for col in range(4):
                    value = self.matrix[row, col]
                    if value != 0:
                        color = BLOCK_COLORS[value]
                        self.cells[row][col]["frame"].configure(bg=color)
                        self.cells[row][col]["number"].configure(
                            bg=color,
                            fg=BLOCK_NUM_COLORS[value],
                            font=BLOCK_NUMBER_FONTS[value],
                            text=str(value))
        self.score = 0
        for row in range(len(self.matrix)):
            #print(self.matrix[row])
            pass

#! _________________________ Possible Move Checker _________________________

    def horizontal_move_exists(self) -> bool:
        return np.any(self.matrix[:, :-1] == self.matrix[:, 1:])

    def vertical_move_exists(self) -> bool:
        return np.any(self.matrix[:-1, :] == self.matrix[1:, :])

#!_________________________ Random Tile Function _________________________

    def add_new_tile(self) -> None:
        #* Checks for if no space is availiable for a new tile to spawn
        if not np.any(self.matrix == 0):
            print("NO SPACE")
            return None
        
        #* randomly selects a tile to spawn new tile. Will only spawn tile if tile empty -> (0)
        row, col = np.random.randint(0, 4, size=2)
        while self.matrix[row, col] != 0:
            row, col = np.random.randint(0, 4, size=2)
        self.matrix[row, col] = np.random.choice([2, 4])

#!_________________________ Update the GUI to match the matrix _________________________

    def update_GUI(self) -> None:
        if self.HEADLESS:
            for row in range(len(self.matrix)):
               # print(self.matrix[row])
                pass
        else:
            for i in range(4):
                for j in range(4):
                    cell_value = self.matrix[i, j]
                    if cell_value == 0:
                        self.cells[i][j]["frame"].configure(bg=EMPTY_COLOR)
                        self.cells[i][j]["number"].configure(
                            bg=EMPTY_COLOR, text="")
                    else:
                        self.cells[i][j]["frame"].configure(
                            bg=BLOCK_COLORS[cell_value])
                        self.cells[i][j]["number"].configure(
                            bg=BLOCK_COLORS[cell_value],
                            fg=BLOCK_NUM_COLORS[cell_value],
                            font=BLOCK_NUMBER_FONTS[cell_value],
                            text=str(cell_value))
            self.score_label.configure(text=self.score)
            self.update_idletasks()

#! _________________________ Arrow-Press and Matrix Manipulation Code_________________________
#* Suddenly I want brisket

    """
    All functions below creates a False 4x4 matrix to merge the possible same integers on the called upon
    direction. If the int have been successfully merged then the bool at the cell turns True.
    
    Parameters can be None because of TKinter's way of calling master bind function 
    Also checks if game is over first to prevent edge cases
    """ 
    def left(self, event=None) -> None:
        self.game_over()
        pre_matrix = self.matrix.copy() 
        for i in range(4):
            self.matrix[i] = self.merge_line(self.matrix[i])
        if not np.array_equal(self.matrix, pre_matrix):  #! This is Brute force checking if a valid move was made or not but ¯\_(ツ)_/¯
            self.add_new_tile()
            self.update_GUI()

    def right(self, event=None) -> None:
        self.game_over()
        pre_matrix = self.matrix.copy() 
        for i in range(4):
            self.matrix[i] = np.flip(self.merge_line(np.flip(self.matrix[i])))
        if not np.array_equal(self.matrix, pre_matrix):  #! This is Brute force checking if a valid move was made or not but ¯\_(ツ)_/¯
            self.add_new_tile()
            self.update_GUI()

    def up(self, event=None) -> None:
        self.game_over()
        pre_matrix = self.matrix.copy() 
        for j in range(4):
            self.matrix[:, j] = self.merge_line(self.matrix[:, j])
        if not np.array_equal(self.matrix, pre_matrix):  #! This is Brute force checking if a valid move was made or not but ¯\_(ツ)_/¯
            self.add_new_tile()
            self.update_GUI()

    def down(self, event=None) -> None:
        self.game_over()
        pre_matrix = self.matrix.copy() 
        for j in range(4):
            self.matrix[:, j] = np.flip(self.merge_line(np.flip(self.matrix[:, j])))
        if not np.array_equal(self.matrix, pre_matrix):  #! This is Brute force checking if a valid move was made or not but ¯\_(ツ)_/¯
            self.add_new_tile()
            self.update_GUI()

    def merge_line(self, line):
        merged = np.zeros(4, dtype=int)
        idx = 0
        for i in range(4):
            if line[i] != 0:
                if merged[idx] == line[i]:
                    merged[idx] *= 2
                    self.score += merged[idx]
                    idx += 1
                elif merged[idx] == 0:
                    merged[idx] = line[i]
                else:
                    idx += 1
                    merged[idx] = line[i]
        return merged

#! _________________________  Result _________________________
    """
    This destroys the window if user achieves 2048 in ANY of the cells 
    OR there is no valid move availiable
    """
    def game_over(self) -> bool:
        is_game_over = False
        if np.any(self.matrix == 2048):
            #print("WIN")
            if not self.HEADLESS:
                self.destroy_window()
            is_game_over = True
        elif not np.any(self.matrix == 0) and not self.horizontal_move_exists() and not self.vertical_move_exists():
            #print("LOSE")
            if not self.HEADLESS:
                self.destroy_window()
            is_game_over = True
        return is_game_over

    def flatten_board_to_list(self) -> list:
        return [element for row in self.matrix for element in row]

    def get_highest_tile(self) -> int:
        return max(max(row) for row in self.matrix)    

def eval_genome(genome, config):
    genome.fitness = 0
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    game = Game(INIT_HEADLESS=True, INIT_TRAINING=True)
    moves_stuck = 0
    prev_score = 0
    seen_states = list()
    while not game.game_over():
        inputs = game.flatten_board_to_list()
        output = net.activate(inputs)
        move = output.index(max(output))
        # Make a move
        if move == 0:
            game.left(None)
        elif move == 1:
            game.right(None)
        elif move == 2:
            game.up(None)
        elif move == 3:
            game.down(None)
        # Don't let the game get stuck
        if game.score == prev_score:
            moves_stuck += 1
            #genome.fitness -= 50
        else:
            moves_stuck = 0
        if game.score < prev_score:
            genome.fitness -= 50
        if moves_stuck > 3:
            #genome.fitness -= 50
            pass
        if moves_stuck > 10:
            genome.fitness -= 50
            break
        # Reward the genome for increasing the score
        if game.score > prev_score:
            genome.fitness += 200
        prev_score = game.score

    return genome.fitness
    #return fitness

def run_neat(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Use ParallelEvaluator to evaluate genomes in parallel
    #parallel_evaluator = ParallelEvaluator(multiprocessing.cpu_count(), eval_genome)
    num_workers = multiprocessing.cpu_count()
    #num_workers = 8
    timeout = 300  # seconds
    parallel_evaluator = ParallelEvaluator(num_workers, eval_genome, timeout=timeout)
    print(f"Training with {num_workers} workers in the pool.")
    
    winner = p.run(parallel_evaluator.evaluate, 1000)
    return winner


def play_with_winner(winner, config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)
    net = neat.nn.FeedForwardNetwork.create(winner, config)

    game = Game(INIT_HEADLESS=True, INIT_TRAINING=False)

    print("Playing with winner")
    previous_score = 0
    moves_without_score_increase = 0
    while not game.game_over():
       inputs = game.flatten_board_to_list()
       output = net.activate(inputs)
       move = output.index(max(output))
       if move == 0:
            game.left(None)
       elif move == 1:
            game.right(None)
       elif move == 2:
            game.up(None)
       elif move == 3:
            game.down(None)
        # game.update_GUI()
        # Don't get stuck
       if game.score == previous_score:
            moves_without_score_increase += 1
       else:
            moves_without_score_increase = 0
       if moves_without_score_increase > 10:
            print("Stuck")
            break
       previous_score = game.score

    # game.update_GUI()
    print(f"Score: {game.score}")
    print(f"Highest Tile: {game.get_highest_tile()}")

if __name__ == "__main__":
    if not TRAINING:
        Game()
    else:
        config_file = "C:/Users/zak/OneDrive/Desktop/CS470/2048-Game-For-CS470/neat_config"
        winner = run_neat(config_file)
        # print(winner)
        play_with_winner(winner, config_file)
