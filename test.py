import chess


def column(matrix, i):
    """
    a quality of life function that grabs the i-th column from a matrix
    :param matrix:
    :param i:
    :return:
    """
    return [row[i] if i < len(row) else 0 for row in matrix]


def fen_to_matrix(board):
    """

    :param board:
    :return: board as a matrix of characters
    """
    if not isinstance(board, chess.Board):
        raise TypeError(board, " is not a chess.Board")

    sfen = str(board.board_fen()).split("/")
    m = []
    for l in sfen:
        print("l: ", l)
        row = []
        for item in l:
            if str(item).isalpha():
                row.append(item)
            elif int(item):
                print(item)
                for i in range(int(item)):
                    row.append("0")
        m.append(row)
    return m


def count_isolated_pawns(board):
    """
    evaluates the number of isolated pawns on the board given

    :param board: the board state to be evaluated for isolated pawns
    :return: if no color specified, returns count of all isolated pawns
    """
    if not isinstance(board, chess.Board):
        raise TypeError(board, " is not a chess.Board")

    m = fen_to_matrix(board)
    white_iso = 0
    black_iso = 0

    for rank in range(len(m)):
        for file in range(len(m[rank])):
            piece = m[rank][file]
            if str(piece) == "p":
                left_file = False
                right_file = False
                if file > 0:
                    left_file = column(m, file - 1)
                if file < 8:
                    right_file = column(m, file + 1)

                left_pawn = "p" in left_file if left_file is not False else False
                if not left_pawn:
                    print("left_file: ", left_file)
                right_pawn = "p" in right_file if right_file is not False else False
                if not right_pawn:
                    print("right_file: ", right_file)

                black_iso += not (left_pawn or right_pawn)

            elif str(piece) == "P":
                left_file = False
                right_file = False
                if file > 0:
                    left_file = column(m, file - 1)
                if file < 8:
                    right_file = column(m, file + 1)

                left_pawn = "P" in left_file if left_file is not False else False
                right_pawn = "P" in right_file if right_file is not False else False
                white_iso += not (left_pawn or right_pawn)

    return white_iso - black_iso


def main():
    b = chess.Board(fen='r3k2r/pp1n2p1/2p2q1p/2b1p3/4B1b1/2PP1N2/PP3PPP/R1BQ1RK1 w KQkq - 0 1')
    print(b)
    print(count_isolated_pawns(b))


if __name__ == "__main__":
    main()
