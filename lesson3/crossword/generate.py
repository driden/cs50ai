import sys

from crossword import *
import queue as q


class CrosswordCreator:
    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy() for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont

        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size, self.crossword.height * cell_size),
            "black",
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                rect = [
                    (j * cell_size + cell_border, i * cell_size + cell_border),
                    (
                        (j + 1) * cell_size - cell_border,
                        (i + 1) * cell_size - cell_border,
                    ),
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (
                                rect[0][0] + ((interior_size - w) / 2),
                                rect[0][1] + ((interior_size - h) / 2) - 10,
                            ),
                            letters[i][j],
                            fill="black",
                            font=font,
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        self.domains = {
            variable: {val for val in values if len(val) == variable.length}
            for variable, values in self.domains.items()
        }

    def revise(self, x: Variable, y: Variable):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps[x, y]

        if not overlap:
            return

        i = overlap[0]
        j = overlap[1]

        previous_length = len(self.domains[x])
        self.domains[x] = {
            wordx
            for wordx in self.domains[x]
            if any([wordx[i] == wordy[j] for wordy in self.domains[y]])
        }

        return previous_length != len(self.domains[x])

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = q.Queue()

        if not arcs or len(arcs) == 0:
            # need to use all
            for var1 in self.domains.keys():
                for var2 in self.domains.keys():
                    if var1 != var2:
                        queue.put((var1, var2))
        else:
            # use arcs passed in
            for arc in arcs:
                queue.put(arc)

        while queue.qsize() > 0:
            x, y = queue.get()

            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False

                for neighbor in self.crossword.neighbors(x) - {y}:
                    queue.put((neighbor, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        raise NotImplementedError

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        raise NotImplementedError

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        raise NotImplementedError


def main():
    # Check usage
    # if len(sys.argv) not in [3, 4]:
    #     sys.exit("Usage: python generate.py structure words [output]")
    #
    # # Parse command-line arguments
    # structure = sys.argv[1]
    # words = sys.argv[2]
    # output = sys.argv[3] if len(sys.argv) == 4 else None
    #
    # # Generate crossword
    # crossword = Crossword(structure, words)
    # creator = CrosswordCreator(crossword)
    # assignment = creator.solve()
    #
    # # Print result
    # if assignment is None:
    #     print("No solution.")
    # else:
    #     creator.print(assignment)
    #     if output:
    #         creator.save(assignment, output)

    crossword = Crossword("data/test_structure0.txt", "data/test_words1.txt")
    creator = CrosswordCreator(crossword)
    creator.domains = {
        Variable(0, 1, "across", 5): {"TODAY", "READY", "HELLO", "AMAZE", "FORGE"},
        Variable(0, 2, "down", 3): {"ODE", "ELM"},
        Variable(2, 1, "across", 5): {"TODAY", "READY", "HELLO", "AMAZE", "FORGE"},
    }

    creator.ac3(arcs=[])

    # x = Variable(0, 1, "across", 5)
    # y = Variable(0, 2, "down", 3)
    # for i in range(crossword.height):
    #     for j in range(crossword.width):
    #         # if (i, j) == overlap:
    #         #     print("o", end="")
    #         if (i, j) in x.cells and (i, j) in y.cells:
    #             print("@", end="")
    #             overlap = i, j
    #         elif (i, j) in x.cells:
    #             print("x", end="")
    #         elif (i, j) in y.cells:
    #             print("y", end="")
    #         else:
    #             print("_", end="")
    #     print("")
    #
    # print(f"{crossword.overlaps[x,y]=}")


if __name__ == "__main__":
    main()
