"""
Tic Tac Toe Player
"""

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
    x_count = 0
    o_count = 0
    for row in board:
        for cell in row:
            if cell == X:
                x_count += 1
            if cell == O:
                o_count += 1

    if x_count > o_count:
        return O
    return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    available_actions = set()
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell == EMPTY:
                available_actions.add((i, j))

    return available_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    available_actions = actions(board)

    copy_board = [row[:] for row in board]

    if action not in available_actions:
        raise InvalidActionError(action, board, "Action is not available")

    i, j = action

    board_range = [x for x in range(3)]

    if i not in board_range or j not in board_range:
        raise InvalidActionError(action, board, "Action out of table")

    copy_board[i][j] = player(copy_board)
    return copy_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for row in range(3):
        if board[row][0] is not None and board[row][0] == board[row][1] == board[row][2]:
            return board[row][0]

    for col in range(3):
        if board[0][col] is not None and board[0][col] == board[1][col] == board[2][col]:
            return board[0][col]

    if board[0][0] is not None and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]

    if board[0][2] is not None and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    return len(actions(board)) == 0 or winner(board) is not None


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    if winner(board) == O:
        return -1
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    plr = player(board)
    print(f"player: {plr}")
    available_actions = actions(board)

    candidates = []

    if plr == X:
        for action in available_actions:
            candidates.append((action, min_function(result(board, action))))

        print(f"candidates: {candidates}")
        best_candidate = candidates[0]

        for candidate in candidates:
            if candidate[1] > best_candidate[1]:
                best_candidate = candidate

        print(f"best_candidate: {best_candidate}")
        return best_candidate[0]

    for action in available_actions:
        candidates.append((action, max_function(result(board, action))))

    print(f"candidates: {candidates}")
    best_candidate = candidates[0]

    for candidate in candidates:
        if candidate[1] < best_candidate[1]:
            best_candidate = candidate

    print(f"best_candidate: {best_candidate}")
    return best_candidate[0]


def min_function(board) -> int:
    if terminal(board):
        return utility(board)
    v = float("inf")

    for action in actions(board):
        v = min(v, max_function(result(board, action)))

    return v


def max_function(board) -> int:
    if terminal(board):
        return utility(board)
    v = float("-inf")

    for action in actions(board):
        v = max(v, min_function(result(board, action)))
    return v


class InvalidActionError(Exception):
    def __init__(self, action, board, message):
        print('InvalidActionError: ', message, 'Action: ', action, 'on board: ', board)