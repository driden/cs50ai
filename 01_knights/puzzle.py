from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    Implication(AKnight, And(AKnave, AKnight)),
    Implication(AKnave, Not(And(AKnave, AKnight))),
    Not(And(AKnight,AKnave)),
    Or(AKnight,AKnave)
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    Implication(AKnight, And(AKnave, BKnave)),
    Implication(AKnave, Not(And(AKnave, BKnave))),
    Not(And(AKnight,AKnave)),
    Or(AKnight,AKnave),
    Not(And(BKnight,BKnave)),
    Or(BKnight,BKnave),
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # A says "We are the same kind."
    Implication(AKnight, Or(And(AKnight, BKnight), And(BKnave,AKnave))),
    Implication(AKnave, Not(Or(And(AKnight, BKnight), And(BKnave,AKnave)))),
    # B says "We are of different kinds."
    Implication(BKnight, Or(And(AKnight, BKnave), And(AKnave, BKnight))),

    # Either a knight or knave
    Not(And(AKnight,AKnave)),
    Or(AKnight,AKnave),
    Not(And(BKnight,BKnave)),
    Or(BKnight,BKnave),
    Implication(Not(AKnight), AKnave),
    Implication(Not(BKnight), BKnave),
    Implication(Not(BKnave), BKnight),
    Implication(Not(BKnight), BKnave),
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    # B says "A said 'I am a knave'."
    # Either B tells the truth and one of this happens:
    #   - A tells the truth and is a knave, (AKnight & AKnave)
    #   - A lies and therefore is a knight  (AKnave & Not(AKnave))
    # Or B is a knave and we negate the prior

    Or(And(BKnight, Or(And(AKnight, AKnave), And(AKnave, Not(AKnave)))), 
       And(BKnave, Not(Or(And(AKnight, AKnave), And(AKnave, Not(AKnave)))))),


    # B says "C is a knave."
    Implication(BKnight, CKnave),
    Implication(Not(BKnight), Not(CKnave)),

    # C says "A is a knight."
    Implication(CKnight, AKnight),
    Implication(Not(CKnight), Not(AKnight)),

    # Either a knight or knave
    And(Or(AKnight,AKnave), Not(And(AKnight,AKnave))),
    Implication(Not(AKnight), AKnave),
    Implication(Not(BKnight), BKnave),

    And(Or(BKnight,BKnave), Not(And(BKnight,BKnave))),
    Implication(Not(BKnight), BKnave),
    Implication(Not(BKnave), BKnight),

    And(Or(CKnight,CKnave), Not(And(CKnight,CKnave))),
    Implication(Not(CKnight), CKnave),
    Implication(Not(CKnave), CKnight),
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
