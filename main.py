import chess


def main():
    print("hello")
    b = chess.Board()
    print(b.legal_moves)
    b.push_san("Nh3")
    print(b.legal_moves)
    print(b)


if __name__ == "__main__":
    main()
