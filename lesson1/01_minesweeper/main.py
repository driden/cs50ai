import minesweeper as ms

def main():
    ai = ms.MinesweeperAI(height=4, width=5)
    ai.add_knowledge((0, 1), 1)
    ai.add_knowledge((1, 0), 1)
    ai.add_knowledge((1, 2), 1)
    ai.add_knowledge((3, 1), 0)
    ai.add_knowledge((0, 4), 0)
    ai.add_knowledge((3, 4), 0)
    safes = [(0, 0), (0, 2)]
    print(ai.safes)



if __name__ == "__main__":
    main()
