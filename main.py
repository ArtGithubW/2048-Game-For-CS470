import tkinter as tk
import random
from config import *
import sys
import keyboard as kb
#from time import time #! Debugging time complexity for the implementation
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
        
    def Init_GUI(self,Headless) -> None:
        if Headless:
            pass
        else:
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
        if self.HEADLESS:
            self.matrix = [[0] * 4 for _ in range(4)]

            # fill 2 random cells with 2s
            row = random.randint(0, 3)
            col = random.randint(0, 3)
            self.matrix[row][col] = random.choice([2, 4])    
            while(self.matrix[row][col] != 0):
                row = random.randint(0, 3)
                col = random.randint(0, 3)
            self.matrix[row][col] = random.choice([2, 4])    
        else:
            self.matrix = [[0] * 4 for _ in range(4)]
            # fill 2 random cells with 2s
            row = random.randint(0, 3)
            col = random.randint(0, 3)
            self.matrix[row][col] = random.choice([2, 4])    
            self.cells[row][col]["frame"].configure(bg=BLOCK_COLORS[2])
            self.cells[row][col]["number"].configure(
                bg=BLOCK_COLORS[2],
                fg=BLOCK_NUM_COLORS[2],
                font=BLOCK_NUMBER_FONTS[2],
                text="2")
            while(self.matrix[row][col] != 0):
                    row = random.randint(0, 3)
                    col = random.randint(0, 3)
            self.matrix[row][col] = random.choice([2, 4])    
            self.cells[row][col]["frame"].configure(bg=BLOCK_COLORS[2])
            self.cells[row][col]["number"].configure(
                bg=BLOCK_COLORS[2],
                fg=BLOCK_NUM_COLORS[2],
                font=BLOCK_NUMBER_FONTS[2],
                text="2")
        self.score = 0
        for row in range(len(self.matrix)):
            print(self.matrix[row])

#! _________________________ Possible Move Checker _________________________

    def horizontal_move_exists(self) -> bool:
        for i in range(4):
            for j in range(3):
                if self.matrix[i][j] == self.matrix[i][j + 1]:
                    return True
        return False


    def vertical_move_exists(self) -> bool:
        for i in range(3):
            for j in range(4):
                if self.matrix[i][j] == self.matrix[i + 1][j]:
                    return True
        return False

#!_________________________ Random Tile Function _________________________

    def add_new_tile(self) -> None:
        #* Checks for if no space is availiable for a new tile to spawn
        if all(element != 0 for row in self.matrix for element in row): 
            print("NO SPACE")
            return None
        
        #* randomly selects a tile to spawn new tile. Will only spawn tile if tile empty -> (0)
        row = random.randint(0, 3)
        col = random.randint(0, 3)
        while(self.matrix[row][col] != 0):
            row = random.randint(0, 3)
            col = random.randint(0, 3)
        self.matrix[row][col] = random.choice([2, 4])


#!_________________________ Update the GUI to match the matrix _________________________

    def update_GUI(self) -> None:
        if self.HEADLESS:
            for row in range(len(self.matrix)):
                print(self.matrix[row])
        else:
            for i in range(len(self.matrix)):
                for j in range(len(self.matrix[0])):
                    cell_value = self.matrix[i][j]
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
    def left(self,event:None):
        self.game_over()
        merged = [[False for _ in range(4)] for _ in range(4)]
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[0])):
                shift = 0
                for q in range(j):
                    if self.matrix[i][q] == 0:
                        shift += 1
                if shift > 0:
                    self.matrix[i][j - shift] = self.matrix[i][j]
                    self.matrix[i][j] = 0
                if self.matrix[i][j - shift] == self.matrix[i][j - shift - 1] and not merged[i][j - shift - 1] \
                        and not merged[i][j - shift]:
                    self.matrix[i][j - shift - 1] *= 2
                    self.score += self.matrix[i][j - shift - 1]
                    self.matrix[i][j - shift] = 0
                    merged[i][j - shift - 1] = True
        self.add_new_tile()
        self.update_GUI()


    def right(self, event:None):
        self.game_over()
        merged = [[False for _ in range(4)] for _ in range(4)]
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[0])):
                shift = 0
                for q in range(j):
                    if self.matrix[i][3 - q] == 0:
                        shift += 1
                if shift > 0:
                    self.matrix[i][3 - j + shift] = self.matrix[i][3 - j]
                    self.matrix[i][3 - j] = 0
                if 4 - j + shift <= 3:
                    if self.matrix[i][4 - j + shift] == self.matrix[i][3 - j + shift] and not merged[i][4 - j + shift] \
                            and not merged[i][3 - j + shift]:
                        self.matrix[i][4 - j + shift] *= 2
                        self.score += self.matrix[i][4 - j + shift]
                        self.matrix[i][3 - j + shift] = 0
                        merged[i][4 - j + shift] = True
        self.add_new_tile()                
        self.update_GUI()

    def up(self, event:None):
        self.game_over()
        merged = [[False for _ in range(4)] for _ in range(4)]
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[0])):
                shift = 0
                if i > 0:
                    for q in range(i):
                        if self.matrix[q][j] == 0:
                            shift += 1
                    if shift > 0:
                        self.matrix[i - shift][j] = self.matrix[i][j]
                        self.matrix[i][j] = 0
                    if self.matrix[i - shift - 1][j] == self.matrix[i - shift][j] and not merged[i - shift][j] \
                            and not merged[i - shift - 1][j]:
                        self.matrix[i - shift - 1][j] *= 2
                        self.score += self.matrix[i - shift - 1][j]
                        self.matrix[i - shift][j] = 0
                        merged[i - shift - 1][j] = True
        self.add_new_tile()                
        self.update_GUI()

    def down(self,event:None):
        self.game_over()
        merged = [[False for _ in range(4)] for _ in range(4)]
        for i in range(3):
            for j in range(4):
                shift = 0
                for q in range(i + 1):
                    if self.matrix[3 - q][j] == 0:
                        shift += 1
                if shift > 0:
                    self.matrix[2 - i + shift][j] = self.matrix[2 - i][j]
                    self.matrix[2 - i][j] = 0
                if 3 - i + shift <= 3:
                    if self.matrix[2 - i + shift][j] == self.matrix[3 - i + shift][j] and not merged[3 - i + shift][j] \
                            and not merged[2 - i + shift][j]:
                        self.matrix[3 - i + shift][j] *= 2
                        self.score += self.matrix[3 - i + shift][j]
                        self.matrix[2 - i + shift][j] = 0
                        merged[3 - i + shift][j] = True
        self.add_new_tile()
        self.update_GUI()


#! _________________________  Result _________________________
    """
    This destroys the window if user achieves 2048 in ANY of the cells 
    OR there is no valid move availiable
    """
    def game_over(self) -> None:
        if self.HEADLESS:
            if any(2048 in row for row in self.matrix):
                print("Win")
                sys.exit()
            elif not any(0 in row for row in self.matrix) and not self.horizontal_move_exists() and not self.vertical_move_exists():
                print("Lose")
                sys.exit()
            else:  #! Delete this in implementation
                print("Debug")
        else:
            if any(2048 in row for row in self.matrix):
                print("Win")
                self.master.destroy()
            elif not any(0 in row for row in self.matrix) and not self.horizontal_move_exists() and not self.vertical_move_exists():
                print("Lose")
                self.master.destroy()

            else: #! Delete this in implementation
                print("Debug")
        
            

def main():
    Game()


if __name__ == "__main__":
    main()