import tkinter as tk
from tkinter import ttk
import numpy as np
from threading import Thread
from queue import Queue


player_type = ['human', 'AI: Min-Max', 'AI: alpha-beta']

def alpha_beta_decision(board, turn, queue):
    possible_moves = board.get_possible_moves()
    best_move = possible_moves[0]
    best_value = -2
    alpha = -2
    beta = 2
    for move in possible_moves:
        updated_board = board.copy()
        updated_board.grid[move[0]][move[1]] = turn % 2 + 1
        value = min_value_ab(updated_board, turn + 1, alpha, beta)
        if value > best_value:
            best_value = value
            best_move = move
    queue.put(best_move)

def max_value_ab(board, turn, alpha, beta):
    if board.check_victory(update_display=False):
        return -1
    if turn > 9:
        return 0
    possible_moves = board.get_possible_moves()
    value = -2
    for move in possible_moves:
        updated_board = board.copy()
        updated_board.grid[move[0]][move[1]] = turn % 2 + 1
        value = max(value, min_value_ab(updated_board, turn + 1, alpha, beta))
        if value >= beta:
            return value
        alpha = max(alpha, value)
    return value

def min_value_ab(board, turn, alpha, beta):
    if board.check_victory(update_display=False):
        return 1
    if turn > 9:
        return 0
    possible_moves = board.get_possible_moves()
    value = 2
    for move in possible_moves:
        updated_board = board.copy()
        updated_board.grid[move[0]][move[1]] = turn % 2 + 1
        value = min(value, max_value_ab(updated_board, turn + 1, alpha, beta))
        if value <= alpha:
            return value
        beta = min(beta, value)
    return value

def minimax_decision(board, turn, queue):
    possible_moves = board.get_possible_moves()
    best_move = possible_moves[0]
    best_value = -2
    for move in possible_moves:
        updated_board = board.copy()
        updated_board.grid[move[0]][move[1]] = turn % 2 + 1
        value = min_value(updated_board, turn + 1)
        if value > best_value:
            best_value = value
            best_move = move
    queue.put(best_move)

def max_value(board, turn):
    if board.check_victory(update_display=False):
        return -1
    if turn > 9:
        return 0
    possible_moves = board.get_possible_moves()
    best_value = -2
    for move in possible_moves:
        updated_board = board.copy()
        updated_board.grid[move[0]][move[1]] = turn % 2 + 1
        value = min_value(updated_board, turn + 1)
        if value > best_value:
            best_value = value
    return best_value

def min_value(board, turn):
    if board.check_victory(update_display=False):
        return 1
    if turn > 9:
        return 0
    possible_moves = board.get_possible_moves()
    worst_value = 2
    for move in possible_moves:
        updated_board = board.copy()
        updated_board.grid[move[0]][move[1]] = turn % 2 + 1
        value = max_value(updated_board, turn + 1)
        if value < worst_value:
            worst_value = value
    return worst_value


class Board:
    grid = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    drawn_symbols = [['', '', ''], ['', '', ''], ['', '', '']]

    def copy(self):
        new_board = Board()
        new_board.grid = np.array(self.grid, copy=True)
        return new_board

    def get_possible_moves(self):
        possible_moves = list()
        for i in range(3):
            for j in range(3):
                if self.grid[i][j] == 0:
                    possible_moves.append((i, j))
        return possible_moves

    def reinit(self):
        # Clear grid
        for i in range(3):
            for j in range(3):
                if self.drawn_symbols[i][j] != '':
                    canvas1.delete(self.drawn_symbols[i][j])
                    self.drawn_symbols[i][j] = ''
        self.grid.fill(0)

    def draw_symbol(self, x, y, symbol):
        self.drawn_symbols[x][y] = canvas1.create_text((x + 0.5) * (width // 3), (y + 0.5) * (height // 3),
                            font=("helvetica", width // 6), text=symbol,
                            fill='black')


    def check_victory(self, update_display=True):
        # Checking lines
        for i in range(3):
            if self.grid[0][i] == self.grid[1][i] == self.grid[2][i] != 0:
                if update_display:
                    for j in range(3):
                        canvas1.itemconfig(self.drawn_symbols[j][i], fill='red')
                return True
        # Checking columns
        for i in range(3):
            if self.grid[i][0] == self.grid[i][1] == self.grid[i][2] != 0:
                if update_display:
                    for j in range(3):
                        canvas1.itemconfig(self.drawn_symbols[i][j], fill='red')
                return True
        # Checking diagonals
        if self.grid[0][0] == self.grid[1][1] == self.grid[2][2] != 0:
            if update_display:
                for i in range(3):
                    canvas1.itemconfig(self.drawn_symbols[i][i], fill='red')
            return True
        if self.grid[0][2] == self.grid[1][1] == self.grid[2][0] != 0:
            if update_display:
                for i in range(3):
                    canvas1.itemconfig(self.drawn_symbols[i][2 - i], fill='red')
            return True
        return False

class TicTacToe:
    symbols = [" ", "O", "X"]
    turn = 1
    players = (0, 0)

    def __init__(self, info_label):
        self.board = Board()
        self.human_turn = False
        self.information_label = info_label
        self.ai_move = Queue()

    def current_player(self):
        return (self.turn-1) % 2 + 1

    def launch(self):
        self.board.reinit()
        self.turn = 0
        self.information_label['text'] = "Turn " + str(self.turn) + " - Player "+str(self.current_player())+" is playing"
        self.information_label['fg'] = 'black'
        self.players = (combobox_player1.current(), combobox_player2.current())
        self.handle_turn()

    def ai_turn(self, ai_type):
        if ai_type == 1:  # Min-Max
            t = Thread(target=minimax_decision, args=(self.board, self.turn, self.ai_move))
            t.start()
            self.ai_wait_for_move()
        elif ai_type == 2:  # Alpha-Beta
            t = Thread(target=alpha_beta_decision, args=(self.board, self.turn, self.ai_move))
            t.start()
            self.ai_wait_for_move()

    def ai_wait_for_move(self):
        if not self.ai_move.empty():
            move = self.ai_move.get()
            self.move(move[0], move[1])
        else:
            window.after(100, self.ai_wait_for_move)

    def click(self, event):
        if self.human_turn:
            x = event.x // (width // 3)
            y = event.y // (height // 3)
            self.move(x, y)

    def move(self, x, y):
        player = self.turn % 2 + 1
        if self.board.grid[x][y] == 0:
            self.board.grid[x][y] = player
            self.board.draw_symbol(x, y, self.symbols[self.turn % 2 + 1])
            self.handle_turn()


    def handle_turn(self):
        self.human_turn = False
        if self.board.check_victory() or self.turn == 9:
            self.information_label['fg'] = 'red'
            if self.board.check_victory():
                self.information_label['text'] = "Player " + str((self.turn - 1) % 2 + 1) + " wins !"
            else:
                self.information_label['text'] = "This is a draw !"
            return
        self.turn = self.turn + 1
        self.information_label['text'] = "Turn " + str(self.turn) + " - Player " + str(
            (self.turn - 1) % 2 + 1) + " is playing"
        if self.players[self.current_player() - 1] != 0:
            self.human_turn = False
            self.ai_turn(self.players[self.current_player() - 1])
        else:
            self.human_turn = True

# Graphical settings
width = 300
height = 300
grid_thickness = 5

window = tk.Tk()
window.title("Tie Tac Toe")
canvas1 = tk.Canvas(window, bg="white", width=width, height=height)



# Grid drawing
line1 = canvas1.create_line(0, height // 3, width, height // 3, fill='black', width=grid_thickness)
line2 = canvas1.create_line(0, (height // 3) * 2, width, (height // 3) * 2, fill='black', width=grid_thickness)
line3 = canvas1.create_line(width // 3, 0, width // 3, height, fill='black', width=grid_thickness)
line4 = canvas1.create_line((width // 3) * 2, 0, (width // 3) * 2, height, fill='black', width=grid_thickness)
canvas1.grid(row=0, column=0, columnspan=2)

information = tk.Label(window, text="")
information.grid(row=1, column=0, columnspan=2)

# Game init
game = TicTacToe(information)

label_player1 = tk.Label(window, text="Player 1: ")
label_player1.grid(row=2, column=0)
combobox_player1 = ttk.Combobox(window, state='readonly')
combobox_player1.grid(row=2, column=1)

label_player2 = tk.Label(window, text="Player 2: ")
label_player2.grid(row=3, column=0)
combobox_player2 = ttk.Combobox(window, state='readonly')
combobox_player2.grid(row=3, column=1)

combobox_player1['values'] = player_type
combobox_player1.current(0)
combobox_player2['values'] = player_type
combobox_player2.current(1)

button2 = tk.Button(window, text='New game', command=game.launch)
button2.grid(row=4, column=0)

button = tk.Button(window, text='Quit', command=window.destroy)
button.grid(row=4, column=1)

# Mouse handling
canvas1.bind('<Button-1>', game.click)

window.mainloop()
