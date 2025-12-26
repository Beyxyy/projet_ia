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
