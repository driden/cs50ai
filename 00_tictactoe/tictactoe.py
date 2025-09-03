"""
Tic Tac Toe Player
"""

import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    count = 0
    for col in range(len(board)):
        for row in range(len(board[col])):
            if board[row][col] == EMPTY:
                count+=1
    return X if count % 2 == 1 else O 
    

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    if terminal(board):
        return actions

    for col in range(len(board)):
        for row in range(len(board[col])):
            if board[row][col] == EMPTY:
                actions.add((row,col))
    return actions

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    if action == None:
        return copy.deepcopy(board)

    row,col=action

    if row < 0 or row > 2 or col < 0 or col > 2 or board[row][col] is not None:
        raise Exception("Cant do action")

    new_board = copy.deepcopy(board)
    new_board[row][col]=player(board)

    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    conds = [ [(0,0), (1,0), (2,0)], # horizontal
              [(0,1), (1,1), (2,1)],
              [(0,2), (1,2), (2,2)],

              [(2,0), (2,1), (2,2)], # vert
              [(1,0), (1,1), (1,2)],
              [(0,0), (0,1), (0,2)],

              [(0,0), (1,1), (2,2)], # diag
              [(0,2), (1,1), (2,0)]
             ]
    for cond in conds:
        players = set([board[x][y] for (x,y) in cond])
        if len(players) == 1 and len(players.intersection([None])) == 0:
            return players.pop()

    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    
    if winner(board) is None:
        count = 0
        for col in range(len(board)):
            for row in range(len(board[col])):
                if board[row][col] == EMPTY:
                    count+=1
        if count > 0:
            return False

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    if board is None:
        return 0

    win=winner(board)
    if win is None:
        return 0
    else:
        return -1 if win == O else 1


def minimax_score(board, depth):
    if terminal(board):
        return utility(board)

    if player(board) == X:
        value = -10
        for action in actions(board):
            value = max(value, minimax_score(result(board, action), depth+1))
        return value
    else:
        value = 10
        for action in actions(board):
            value = min(value, minimax_score(result(board, action), depth+1))
        return value

def minimax(board, depth=1):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    # X wants to maximize score
    best_action = None
    acts = actions(board)
    if player(board) == X:
        max = -10
        for action in acts:
            other_player_util = minimax_score(result(board,action), depth+1) # Get the greatest utility

            # If i found an action that maximizes utility
            if other_player_util > max:
                max = other_player_util  
                best_action = action

        return best_action
    else:
        min = 10
        for action in acts:
            other_player_util = minimax_score(result(board,action), depth+1) # Get the greatest utility

            if other_player_util < min:
                min = other_player_util  
                best_action = action
        return best_action

