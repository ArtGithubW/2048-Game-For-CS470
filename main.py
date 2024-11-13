import tkinter as tk
import random
import numpy as np
from config import *
import sys
import keyboard as kb
from time import time #! Debugging time complexity for the implementation
class Game(tk.Frame):
    def __init__(self):
        tk.Frame.__init__(self)
        
        self.HEADLESS = HEADLESS
        
        if self.HEADLESS:
            self.start_game()
            while True:
                self.on_arrow_key()
                
        else:
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
            print(self.matrix[row])

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
                print(self.matrix[row])
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
    def game_over(self) -> None:
        if self.HEADLESS:
            if np.any(self.matrix == 2048):
                print("Win")
                sys.exit()
            elif not np.any(self.matrix == 0) and not self.horizontal_move_exists() and not self.vertical_move_exists():
                print("Lose")
                sys.exit()
            else:  #! Delete this in implementation
                print("Debug")
        else:
            if np.any(self.matrix == 2048):
                print("Win")
                self.master.destroy()
            elif not np.any(self.matrix == 0) and not self.horizontal_move_exists() and not self.vertical_move_exists():
                print("Lose")
                self.master.destroy()
            else: #! Delete this in implementation
                print("Debug")
        
def main():
    Game()

if __name__ == "__main__":
    main()
