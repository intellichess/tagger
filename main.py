import collections

import chess.pgn as c_pgn


def count_isolated_pawns(board, color=None):
    if color is None:
        x = 0
    return 1


def count_singled_pawns(board, color=None):
    return 1


def count_doubled_pawns(board, color=None):
    return 1


def evaluate(board):
    """Claude Shannon's simple symmetric board evaluation.

    f(p) = 200(K-K')
       + 9(Q-Q')
       + 5(R-R')
       + 3(B-B' + N-N')
       + 1(P-P')
       - 0.5(D-D' + S-S' + I-I')
       + 0.1(M-M') + ...

    KQRBNP = number of kings, queens, rooks, bishops, knights and pawns
    D,S,I = doubled, blocked and isolated pawns
    M = Mobility (the number of legal moves)
    """

    piece_counts = collections.Counter(str(board.board_fen()))

    v = 200 * (piece_counts["K"] - piece_counts["k"]) \
        + 9 * (piece_counts["Q"] - piece_counts["q"]) \
        + 5 * (piece_counts["R"] - piece_counts["r"]) \
        + 3 * (piece_counts["B"] - piece_counts["b"] + piece_counts["N"] - piece_counts["n"]) \
        + (piece_counts["P"] - piece_counts["p"]) \
        - 0.5 * (count_doubled_pawns(board) + count_singled_pawns(board) + count_isolated_pawns(board)) \
        + 0.1 * (board.legal_moves.count())

    """
    piece_values = {
        'P': 1, "p": -1,
        'N': 3, "n": -3,
        'B': 3, "b": -3,
        'R': 5, "r": -5,
        'Q': 9, "q": -9,
        'K': 200, "k": -200
    }

    e = 0
    for x in board.board_fen():
        if x.isalpha():
            e += piece_values[x]
    """
    return v


def main():
    morphy = open("data/Morphy.pgn", encoding="utf-8-sig")
    g1 = c_pgn.read_game(morphy)
    print(g1.headers)

    board = g1.board()
    print(board, "\n")

    for move in g1.main_line():
        print(move, evaluate(board))
        board.push(move)
        print(board, "\n")
        input("press enter to continue...\n")


if __name__ == "__main__":
    main()
