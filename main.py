from os import listdir

import chess
import chess.pgn as c_pgn
import collections
import numpy as np
import pandas as pd


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
        row = []
        for item in l:
            if str(item).isalpha():
                row.append(item)
            elif int(item):
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

                left_pawn = "p" in left_file if left_file is not False else None
                right_pawn = "p" in right_file if right_file is not False else None
                black_iso += not (left_pawn or right_pawn)

            elif str(piece) == "P":
                left_file = False
                right_file = False
                if file > 0:
                    left_file = column(m, file - 1)
                if file < 8:
                    right_file = column(m, file + 1)

                left_pawn = "P" in left_file if left_file is not False else None
                right_pawn = "P" in right_file if right_file is not False else None
                white_iso += not (left_pawn or right_pawn)

    return white_iso - black_iso


def count_blocked_pawns(board):
    """
    Returns the count of blocked pawns on the board.
    :param board:
    :return: count of blocked pawns on the board
    """
    if not isinstance(board, chess.Board):
        raise TypeError(board, " is not a ", type(chess.Board))

    m = fen_to_matrix(board)
    white_blocked = 0
    black_blocked = 0

    for rank in range(len(m)):
        c = column(m, rank)
        # print(c)
        for i in range(1, len(c) - 1):
            piece_c = str(c[i])  # current piece
            piece_n = str(c[i + 1]) if c[i + 1] is not None else None  # next piece
            piece_p = str(c[i - 1]) if c[i - 1] is not None else None  # previous piece
            if piece_c == "p" and piece_n != "0":
                black_blocked += 1
            elif piece_c == "P" and piece_p != "0":
                white_blocked += 1

    return white_blocked - black_blocked


def count_doubled_pawns(board):
    """
    Returns the count of doubled pawns on the board. Does not count tripled or quadrupled.
    :param board:
    :return: count of doubled pawns in board
    """
    if not isinstance(board, chess.Board):
        raise TypeError(board, " is not a ", type(chess.Board))

    m = fen_to_matrix(board)

    white_doubled = 0
    black_doubled = 0
    for rank in range(len(m)):
        ctr = collections.Counter()
        c = column(m, rank)
        ctr.update(c)
        if ctr["p"] == 2:
            black_doubled += 1
        if ctr["P"] == 2:
            white_doubled += 1

    return white_doubled - black_doubled


def evaluate(board):
    """
    Claude Shannon's simple symmetric board evaluation.

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

    :param board: some board state to be evaluated
    :return: an evaluation of the board state via the function given above
    """

    piece_counts = collections.Counter()
    piece_counts.update(str(board.board_fen()))

    v = 200 * (piece_counts["K"] - piece_counts["k"]) \
        + 9 * (piece_counts["Q"] - piece_counts["q"]) \
        + 5 * (piece_counts["R"] - piece_counts["r"]) \
        + 3 * (piece_counts["B"] - piece_counts["b"] + piece_counts["N"] - piece_counts["n"]) \
        + (piece_counts["P"] - piece_counts["p"]) \
        - 0.5 * (count_doubled_pawns(board) + count_blocked_pawns(board) + count_isolated_pawns(board)) \
        + 0.1 * (board.legal_moves.count())

    return v


def get_player_team(filename, game):
    """
    Returns the player's team color
    :param filename: the pgn file named after the player
    :param game: the chess game
    :return:
    """
    filename = ''.join(i for i in filename if not i.isdigit())  # sometimes multiple files will be
    # for the same player, e.g. Alekhine and Alekhine1, so we want to avoid numbers in our player names

    player = ""
    sep = "/"
    if filename.rfind(sep) > 0:
        player = filename[filename.rindex(sep) + 1:-4]
    else:
        player = filename[0:-4]

    return "White" if player in game.headers["White"] else "Black"


def get_new_square(move):
    """
    Gets the square from the move
    :param move: the spot that the piece just moved to
    :return: a square instance of the board
    """
    files = "a,b,c,d,e,f,g,h".split(",")
    move = str(move)
    file = move[2:3]
    rank = move[3:4]

    file = files.index(file)
    rank = int(rank) - 1

    return chess.square(file, rank)


def get_old_square(move):
    """
    Gets the square from the old spot
    :param move: the spot that the piece was at
    :return:  square instance of the board
    """
    files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    move = str(move)
    file = move[0:1]
    rank = move[1:2]

    file = files.index(file)
    rank = int(rank) - 1

    return chess.square(file, rank)


def count_material_threatened(board, squares_threatened, color):
    """
    Gets the material threatened per move
    :param board: board instance
    :param squares_threatened: the spots that the piece can go to
    :param color: piece color
    :return: material threatened by the move
    """

    true_color = chess.WHITE if color == "White" else chess.BLACK
    pieces_threatened = 0
    for piece in squares_threatened:
        file = chess.square_file(piece)
        rank = chess.square_rank(piece)
        square = chess.square(file, rank)
        cur_piece = board.piece_at(square)
        if cur_piece is not None and cur_piece.color is not true_color:
            cur_piece_type = cur_piece.piece_type
            if cur_piece_type == chess.PAWN:  # pawn
                pieces_threatened += 1
            elif cur_piece_type == chess.KNIGHT or cur_piece_type == chess.BISHOP:
                pieces_threatened += 3
            elif cur_piece_type == chess.ROOK:
                pieces_threatened += 5
            elif cur_piece_type == chess.QUEEN:
                pieces_threatened += 9
    return pieces_threatened


def is_gambit_made(board, turn):
    """
    Count the number of gambits made
    :param board: board instance
    :param turn: to make sure move stack isn't null
    :return: a
    """
    if turn >= 3:
        cur_move = board.pop()
        prev_move = board.pop()
        prev_prev_move = board.pop()

        # Getting the spot the piece moved to on the player's previous turn
        board.push(prev_prev_move)
        prev_prev_square = get_new_square(prev_prev_move)

        # Getting the spot the piece moved to on the opposing player's last turn
        board.push(prev_move)
        prev_square = get_new_square(prev_move)

        # Getting the spot the piece moved to on the player's current turn
        board.push(cur_move)
        cur_square = get_new_square(cur_move)

        # This means that on the player's last turn, the player moved a piece, then the opposing player
        # captured that piece, and the player then captured that piece
        return True if (prev_prev_square == prev_square and prev_square == cur_square) else False


def simulate_game(game, color):
    """
    Simulates the game to find material threatened, gambits made, checks made, and moves made
    :param game:
    :param color:
    :return:
    """
    number_of_moves = 0
    material_threatened = 0
    number_of_gambits = 0
    number_of_checks = 0
    sum_board_eval = 0
    turn = 1

    board = game.board()
    # looping through all the moves in the game
    for move in game.main_line():
        # simulating the move
        board.push(move)
        # if it's the player's turn
        if (turn % 2 == 1 and color == "White") or (turn % 2 == 0 and color == "Black"):
            prev_square = get_old_square(move)  # old spot before the current piece moved
            cur_square = get_new_square(move)  # new spot after the current piece moved
            # checking if the move put the enemy's king into check
            cur_move = chess.Move(prev_square, cur_square)
            if board.is_into_check(cur_move):
                number_of_checks += 1
            pieces_threatened = board.attacks(cur_square)  # get all pieces threatened by the move
            # Checking if a gambit was made
            if is_gambit_made(board, turn):
                number_of_gambits += 1
            # count the number of enemy pieces threatened by the move
            material_threatened += count_material_threatened(board, pieces_threatened, color)
            number_of_moves += 1
        sum_board_eval += evaluate(board)
        turn += 1

    stats = {
        "Move Count": number_of_moves,
        "Average Material Threatened": material_threatened / number_of_moves if number_of_moves != 0 else 0,
        "Gambit Count": number_of_gambits,
        "Check Count": number_of_checks,
        "Average Board Evaluation": sum_board_eval / number_of_moves if number_of_moves != 0 else 0
    }

    return stats


def read_games(file):
    headers = [
        "Event", "Site", "Date", "Round", "White", "Black", "Result", "BlackElo", "WhiteElo", "ECO",
        "Move Count", "Average Material Threatened", "Gambit Count", "Check Count", "Average Board Evaluation"
    ]
    df = pd.DataFrame(columns=headers)

    with open(file) as pgn_file:
        i = 1
        while True:
            print(file, " Game ", i)
            game = c_pgn.read_game(pgn_file)
            if game is None:
                break
            color = get_player_team(file, game)
            stats = simulate_game(game, color)
            print(stats)
            d = {**dict(game.headers), **stats}
            df = df.append(d, ignore_index=True)
            i += 1

    return df


def process_aggro():
    aggro = pd.DataFrame()
    for f in listdir("./data/aggressive"):
        # print(read_games("data/aggressive/Morphy.pgn"))
        f = "./data/aggressive/" + str(f)
        aggro = aggro.append(read_games(f))

    # print(aggro.head())
    # print(aggro.shape)
    # print(np.mean(aggro["Average Material Threatened"]))
    # aggro.to_csv("aggressive.csv")
    aggro = aggro[aggro["Average Material Threatened"] != 0]
    return aggro


def process_defen():
    defen = pd.DataFrame()
    for f in listdir("./data/defensive"):
        f = "./data/defensive/" + str(f)
        defen = defen.append(read_games(f))

    # print(defen.head())
    # print(defen.shape)
    # print(np.mean(defen["Average Material Threatened"]))
    # defen.to_csv("defensive.csv")
    defen = defen[defen["Average Material Threatened"] != 0]
    return defen


def update_csvs():
    aggro = process_aggro()
    defen = process_defen()
    print("AGGRESSIVE:", aggro.shape)
    print("Avg Mat Threat", np.mean(aggro["Average Material Threatened"]))
    print("Avg Move Count", np.mean(aggro["Move Count"]))
    print("Avg Gambit Count", np.mean(aggro["Gambit Count"]))
    print("Avg Check Count", np.mean(aggro["Check Count"]))
    print("Avg Avg Board Eval", np.mean(aggro["Average Board Evaluation"]))

    print("DEFENSIVE:", defen.shape)
    print("Avg Mat Threat", np.mean(defen["Average Material Threatened"]))
    print("Avg Move Count", np.mean(defen["Move Count"]))
    print("Avg Gambit Count", np.mean(defen["Gambit Count"]))
    print("Avg Check Count", np.mean(defen["Check Count"]))
    print("Avg Avg Board Eval", np.mean(defen["Average Board Evaluation"]))

    aggro["Aggressive"] = 1
    defen["Aggressive"] = 0

    aggro.to_csv("aggressive.csv")
    defen.to_csv("defensive.csv")


def main():
    update_csvs()


if __name__ == "__main__":
    main()
