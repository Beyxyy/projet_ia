import tkinter as tk
from tkinter import ttk
import numpy as np
import random as rnd
from threading import Thread
from queue import Queue
import math

disk_color = ['white', 'red', 'orange']
disks = list()

player_type = ['human']
for i in range(42):
    player_type.append('AI: alpha-beta level '+str(i+1))

# --- CONSTANTES POUR L'EVALUATION ---
WINDOW_LENGTH = 4
EMPTY = 0

def alpha_beta_decision(board, turn, ai_level, queue, max_player):
    """
    Lance l'algorithme Alpha-Beta.
    ai_level correspond à la profondeur (depth).
    max_player est le numéro du joueur (1 ou 2) qui est l'IA.
    """
    
    # On détermine l'adversaire
    min_player = 1 if max_player == 2 else 2

    def minimax(current_board, depth, alpha, beta, maximizingPlayer):
        valid_locations = current_board.get_possible_moves()
        is_terminal = current_board.check_victory()
        
        # Cas de base : Victoire ou profondeur atteinte
        if is_terminal:
            if maximizingPlayer:
                # Si c'est à nous de jouer mais que c'est une victoire,
                # c'est que l'adversaire vient de jouer et gagner.
                return -100000000000, None
            else:
                return 100000000000, None
        elif depth == 0 or len(valid_locations) == 0:
            return current_board.eval(max_player), None

        if maximizingPlayer:
            value = -math.inf
            best_col = valid_locations[0] # Fallback
            # On trie les coups pour optimiser l'élagage (colonne centrale d'abord)
            valid_locations.sort(key=lambda x: abs(x-3)) 
            
            for col in valid_locations:
                b_copy = current_board.copy()
                b_copy.add_disk(col, max_player, update_display=False)
                new_score, _ = minimax(b_copy, depth - 1, alpha, beta, False)
                
                if new_score > value:
                    value = new_score
                    best_col = col
                
                alpha = max(alpha, value)
                if alpha >= beta:
                    break # Élagage Beta
            return value, best_col

        else: # Minimizing Player (L'adversaire)
            value = math.inf
            best_col = valid_locations[0]
            valid_locations.sort(key=lambda x: abs(x-3))

            for col in valid_locations:
                b_copy = current_board.copy()
                b_copy.add_disk(col, min_player, update_display=False)
                new_score, _ = minimax(b_copy, depth - 1, alpha, beta, True)
                
                if new_score < value:
                    value = new_score
                    best_col = col
                
                beta = min(beta, value)
                if alpha >= beta:
                    break # Élagage Alpha
            return value, best_col

    # Lancement initial
    # Note : ai_level sert de profondeur. Attention, une profondeur > 6 peut être lente en Python pur.
    score, best_col = minimax(board, ai_level, -math.inf, math.inf, True)
    
    # Si pour une raison quelconque best_col est None (ex: match nul inévitable), on prend un coup valide au hasard
    if best_col is None:
        possible = board.get_possible_moves()
        if possible:
            best_col = rnd.choice(possible)

    queue.put(best_col)

class Board:
    # Attention: Le squelette définit la grille comme 7 colonnes de 6 lignes.
    # grid[x][y] où x est la colonne (0-6) et y la ligne (0-5)
    grid = np.array([[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]])

    def evaluate_window(self, window, player):
        score = 0
        opp_player = 1 if player == 2 else 2

        if window.count(player) == 4:
            score += 100
        elif window.count(player) == 3 and window.count(EMPTY) == 1:
            score += 5
        elif window.count(player) == 2 and window.count(EMPTY) == 2:
            score += 2

        # Stratégie défensive : bloquer l'adversaire est prioritaire
        if window.count(opp_player) == 3 and window.count(EMPTY) == 1:
            score -= 4 

        return score

    def eval(self, player):
        """
        Fonction d'évaluation heuristique pour une grille non terminale.
        [cite: 6, 36, 37]
        """
        score = 0
        
        # 1. Prioriser le centre (colonne 3)
        # On récupère la colonne centrale (index 3)
        center_array = list(self.grid[3][:])
        center_count = center_array.count(player)
        score += center_count * 3

        # 2. Évaluation des alignements (Horizontal, Vertical, Diagonal)
        
        # Horizontal (dans le grid du squelette, les colonnes sont le premier index)
        # Il faut itérer sur les lignes (y) puis les colonnes (x)
        for r in range(6):
            row_array = [self.grid[c][r] for c in range(7)] # Construction de la ligne
            for c in range(7 - 3):
                window = row_array[c:c+WINDOW_LENGTH]
                score += self.evaluate_window(window, player)

        # Vertical (plus simple car grid[c] est déjà une colonne)
        for c in range(7):
            col_array = list(self.grid[c])
            for r in range(6 - 3):
                window = col_array[r:r+WINDOW_LENGTH]
                score += self.evaluate_window(window, player)

        # Diagonale positive (/)
        for r in range(6 - 3):
            for c in range(7 - 3):
                window = [self.grid[c+i][r+i] for i in range(WINDOW_LENGTH)]
                score += self.evaluate_window(window, player)

        # Diagonale négative (\)
        for r in range(6 - 3):
            for c in range(7 - 3):
                window = [self.grid[c+i][r+3-i] for i in range(WINDOW_LENGTH)]
                score += self.evaluate_window(window, player)

        return score

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
        # On vérifie le centre d'abord pour optimiser l'IA (heuristique de tri des coups)
        # Mais get_possible_moves doit juste renvoyer la validité
        if self.grid[3][5] == 0:
            possible_moves.append(3)
        for shift_from_center in range(1, 4):
            if self.grid[3 + shift_from_center][5] == 0:
                possible_moves.append(3 + shift_from_center)
            if self.grid[3 - shift_from_center][5] == 0:
                possible_moves.append(3 - shift_from_center)
        return possible_moves

    def add_disk(self, column, player, update_display=True):
        j = 0 # Initialisation par sécurité
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
            if 0 <= column < 7: # Sécurité clic hors zone
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
        if self.board.check_victory():
            information['fg'] = 'red'
            information['text'] = "Player " + str(self.current_player()) + " wins !"
            self.human_turn = False # Bloquer le jeu
            return
        elif self.turn >= 42: # Correction : >= 42 car 42 pions max
            information['fg'] = 'red'
            information['text'] = "This a draw !"
            return
        
        self.turn = self.turn + 1
        self.human_turn = False # Bloquer temporairement
        information['text'] = "Turn " + str(self.turn) + " - Player " + str(
            self.current_player()) + " is playing"
        
        # Si le joueur actuel est une IA (index > 0 dans le combobox)
        if self.players[self.current_player() - 1] != 0:
            self.human_turn = False
            # L'index 0 est Humain, donc niveau 1 = index 1
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
combobox_player2.current(4) # Défaut IA niveau 4

button2 = tk.Button(window, text='New game', command=game.launch)
button2.grid(row=4, column=0)

button = tk.Button(window, text='Quit', command=window.destroy)
button.grid(row=4, column=1)

# Mouse handling
canvas1.bind('<Button-1>', game.click)

window.mainloop()