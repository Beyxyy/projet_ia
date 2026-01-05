import tkinter as tk
from tkinter import ttk
import numpy as np
import random as rnd
from threading import Thread
from queue import Queue


disk_color = ['white', 'red', 'orange']
disks = list()

player_type = ['human']
for i in range(42):
    player_type.append('AI: alpha-beta level '+str(i+1))

def alpha_beta_decision(board, turn, ai_level, queue, max_player):
    value = -float("inf")
    action=board.get_possible_moves()[0]
    for move in board.get_possible_moves() : 
        updated_board = board.copy()
        index = 5
        while index>-1 : 
            #on joue le coup
            if updated_board.grid[move][index] == 0:
                updated_board.grid[move][index] = turn % 2 + 1
                break
            index -= 1
        _beta = float("inf")
        _alpha = -float("inf")
        v_computed = max_value_ab(
            board=updated_board,
            turn_current=turn+1,
            turn_original=turn,
            ia_level=ai_level,
            alpha=_alpha,
            beta=_beta,
            max_player=max_player
        )
        if(value<v_computed) : 
            value=v_computed
            action=move
    queue.put(action)

def max_value_ab(board, turn_current, turn_original, ia_level, alpha, beta, max_player):
    player_precedent = (turn_current - 1) % 2 + 1

    if board.check_victory():
        if player_precedent == max_player:
            return 100
        else:
            return -100
    if turn_current-turn_original==ia_level:
        return board.eval(max_player)
    possible_moves = board.get_possible_moves()
    value = -float("inf")

    #recherche des coups possibles
    for move in possible_moves:
        updated_board = board.copy()
        index = 5
        while index>-1 : 
            #on joue le coup
            if updated_board.grid[move][index] == 0:
                updated_board.grid[move][index] = turn_current % 2 + 1
                break
            index -= 1

        # on fait l'opération d'élagage    
        value = max(value, min_value_ab(board=updated_board, turn_current=turn_current + 1, ia_level=ia_level,turn_original=turn_original, alpha=alpha, beta=beta, max_player=max_player))
        if value >= beta:
            return value
        alpha = max(alpha, value)
    return value

def min_value_ab(board, turn_current, turn_original, ia_level, alpha, beta, max_player):
    player_precedent = (turn_current - 1) % 2 + 1

    if board.check_victory():
        if player_precedent == max_player:
            return 100
        else:
            return -100
    if turn_current-turn_original==ia_level:
        return board.eval(max_player)
    possible_moves = board.get_possible_moves()
    value = float("inf")
    for move in possible_moves:
        updated_board = board.copy()
        index = 5
        while index>-1 : 
            #on joue le coup
            if updated_board.grid[move][index] == 0:
                updated_board.grid[move][index] = turn_current % 2 + 1
                break
            index -= 1
        value = min(value, max_value_ab(board=updated_board, turn_current=turn_current + 1, ia_level=ia_level,turn_original=turn_original, alpha=alpha, beta=beta, max_player=max_player))
        if value <= alpha:
            return value
        beta = min(beta, value)
    return value



class Board:
    grid = np.array([[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]])


    # pour chacun des coups possibles calculer combien mènent à la victoire
    # si aucun alors on regarde lequel a le plus de pions alignés sans counter
    # dans la direction  
    def eval(self, player):
        autre_player = 2 if player == 1 else 1
        score = [0 for i in range(4)]
        final_score = []
        for move in self.get_possible_moves() : 
            updated_board = self.copy()
            index = 5
            while index>-1 : 
                #on joue le coup
                if updated_board.grid[move][index] == 0:
                    updated_board.grid[move][index] = player
                    break
                index -= 1
            if(updated_board.check_victory()) : 
                return 100
            # compte les diagonales, gauche droite et en bas
            #on calcule sur la ligne
            longueur_ligne = 7
            longueur_colonne = 6
            for i in range(longueur_ligne) : 
                        score[0] = score[0] + 1 if updated_board.grid[move][i-1] == player or updated_board.grid[move][i-1] == 0 else 0
            # je check les diagonales en partant du move choisi et de l'index(hauteur dans la colonne) auquel la pièce a été joué
            for decalage_diagonal in range(-3,4) :
                compteur = 0
                for k in range(4) : 
                    x = move + decalage_diagonal + k
                    y = index + decalage_diagonal + k
                    if(x>=0 and x<longueur_ligne and y>=0 and y<longueur_colonne) : 
                            compteur = compteur +1 if updated_board.grid[x][y] == player or updated_board.grid[x][y] == 0 else 0
                score[1] = max(score[1], compteur)
            for decalage_diagonal in range(-3,4) :
                compteur = 0
                for k in range(4) : 
                    x = move + decalage_diagonal + k
                    y = index - decalage_diagonal - k
                    if(x>=0 and x<longueur_ligne and y>=0 and y<longueur_colonne) : 
                            compteur = compteur +1 if updated_board.grid[x][y] == player or updated_board.grid[x][y] == 0 else 0
                score[2] = max(score[2], compteur)
                

            
            # je check les colonnes
            for j in range(longueur_colonne) : 
                for i in range(longueur_ligne -3) : 
                    if(updated_board.grid[i][j] == player and updated_board.grid[i+1][j] == player and updated_board.grid[i+2][j] == player and updated_board.grid[i+3][j] == player) : 
                        score[3] = score[3] +1
            final_score.append(max(score))
        return max(final_score)*25 if final_score else 0

        
    def copy(self):
        new_board = Board()
        new_board.grid = np.array(self.grid, copy=True)
        return new_board

    def reinit(self):
        self.grid.fill(0)
        for i in range(7):
            for j in range(6):
                canvas1.itemconfig(disks[i][j], fill=disk_color[0])

    def get_possible_moves(self):
        possible_moves = list()
        if self.grid[3][5] == 0:
            possible_moves.append(3)
        for shift_from_center in range(1, 4):
            if self.grid[3 + shift_from_center][5] == 0:
                possible_moves.append(3 + shift_from_center)
            if self.grid[3 - shift_from_center][5] == 0:
                possible_moves.append(3 - shift_from_center)
        return possible_moves

    def add_disk(self, column, player, update_display=True):
        for j in range(6):
            if self.grid[column][j] == 0:
                break
        self.grid[column][j] = player
        if update_display:
            canvas1.itemconfig(disks[column][j], fill=disk_color[player])

    def column_filled(self, column):
        return self.grid[column][5] != 0

    def check_victory(self):
        # Horizontal alignment check
        for line in range(6):
            for horizontal_shift in range(4):
                if self.grid[horizontal_shift][line] == self.grid[horizontal_shift + 1][line] == self.grid[horizontal_shift + 2][line] == self.grid[horizontal_shift + 3][line] != 0:
                    return True
        # Vertical alignment check
        for column in range(7):
            for vertical_shift in range(3):
                if self.grid[column][vertical_shift] == self.grid[column][vertical_shift + 1] == \
                        self.grid[column][vertical_shift + 2] == self.grid[column][vertical_shift + 3] != 0:
                    return True
        # Diagonal alignment check
        for horizontal_shift in range(4):
            for vertical_shift in range(3):
                if self.grid[horizontal_shift][vertical_shift] == self.grid[horizontal_shift + 1][vertical_shift + 1] ==\
                        self.grid[horizontal_shift + 2][vertical_shift + 2] == self.grid[horizontal_shift + 3][vertical_shift + 3] != 0:
                    return True
                elif self.grid[horizontal_shift][5 - vertical_shift] == self.grid[horizontal_shift + 1][4 - vertical_shift] ==\
                        self.grid[horizontal_shift + 2][3 - vertical_shift] == self.grid[horizontal_shift + 3][2 - vertical_shift] != 0:
                    return True
        return False


class Connect4:

    def __init__(self):
        self.board = Board()
        self.human_turn = False
        self.turn = 1
        self.players = (0, 0)
        self.ai_move = Queue()

    def current_player(self):
        return 2 - (self.turn % 2)

    def launch(self):
        self.board.reinit()
        self.turn = 0
        information['fg'] = 'black'
        information['text'] = "Turn " + str(self.turn) + " - Player " + str(
            self.current_player()) + " is playing"
        self.human_turn = False
        self.players = (combobox_player1.current(), combobox_player2.current())
        self.handle_turn()

    def move(self, column):
        if not self.board.column_filled(column):
            self.board.add_disk(column, self.current_player())
            self.handle_turn()

    def click(self, event):
        if self.human_turn:
            column = event.x // row_width
            self.move(column)

    def ai_turn(self, ai_level):
        Thread(target=alpha_beta_decision, args=(self.board, self.turn, ai_level, self.ai_move, self.current_player(),)).start()
        self.ai_wait_for_move()

    def ai_wait_for_move(self):
        if not self.ai_move.empty():
            self.move(self.ai_move.get())
        else:
            window.after(100, self.ai_wait_for_move)

    def handle_turn(self):
        self.human_turn = False
        if self.board.check_victory():
            information['fg'] = 'red'
            information['text'] = "Player " + str(self.current_player()) + " wins !"
            return
        elif self.turn >= 42:
            information['fg'] = 'red'
            information['text'] = "This a draw !"
            return
        self.turn = self.turn + 1
        information['text'] = "Turn " + str(self.turn) + " - Player " + str(
            self.current_player()) + " is playing"
        if self.players[self.current_player() - 1] != 0:
            self.human_turn = False
            self.ai_turn(self.players[self.current_player() - 1])
        else:
            self.human_turn = True


game = Connect4()

# Graphical settings
width = 700
row_width = width // 7
row_height = row_width
height = row_width * 6
row_margin = row_height // 10

window = tk.Tk()
window.title("Connect 4")
canvas1 = tk.Canvas(window, bg="blue", width=width, height=height)

# Drawing the grid
for i in range(7):
    disks.append(list())
    for j in range(5, -1, -1):
        disks[i].append(canvas1.create_oval(row_margin + i * row_width, row_margin + j * row_height, (i + 1) * row_width - row_margin,
                            (j + 1) * row_height - row_margin, fill='white'))


canvas1.grid(row=0, column=0, columnspan=2)

information = tk.Label(window, text="")
information.grid(row=1, column=0, columnspan=2)

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
combobox_player2.current(6)

button2 = tk.Button(window, text='New game', command=game.launch)
button2.grid(row=4, column=0)

button = tk.Button(window, text='Quit', command=window.destroy)
button.grid(row=4, column=1)

# Mouse handling
canvas1.bind('<Button-1>', game.click)

window.mainloop()
    