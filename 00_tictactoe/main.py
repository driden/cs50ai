import tictactoe 

X = "X"
O = "O"
EMPTY = None

if __name__ == "__main__":

    # board = [[EMPTY, EMPTY, EMPTY], [X, O, O], [EMPTY, X, EMPTY]]
    board = [[EMPTY, EMPTY, EMPTY], [X, O, O], [EMPTY, X, EMPTY]]
    expected = (2, 0)
    print(tictactoe.minimax(board))

