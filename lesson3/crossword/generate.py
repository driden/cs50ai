import sys

from crossword import *
from copy import deepcopy

Arc = tuple[Variable, Variable]


class CrosswordCreator:
    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword: Crossword = crossword
        self.domains: dict[Variable, set[str]] = {
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

        if overlap is None:
            return False

        i, j = overlap

        previous_length = len(self.domains[x])
        self.domains[x] = {
            wordx
            for wordx in self.domains[x]
            if any([wordx[i] == wordy[j] for wordy in self.domains[y]])
        }

        return previous_length != len(self.domains[x])

    def ac3(self, arcs: list[Arc] | None = None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        if arcs is None:
            arcs = [
                (x, y)
                for x in self.crossword.variables
                for y in self.crossword.neighbors(x)
            ]

        while len(arcs) > 0:
            x, y = arcs.pop()

            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False

                for neighbor in self.crossword.neighbors(x) - {y}:
                    arcs.append((neighbor, x))
        return True

    def assignment_complete(self, assignment: dict[Variable, str]) -> bool:
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        return len(self.domains) == len(assignment)

    def overlap_satisfied(
        self,
        var: Variable,
        neighbor: Variable,
        var_value: str,
        neighbor_value: str,
    ):
        # If no overlap, no arc consistency to satisfy
        if not self.crossword.overlaps[var, neighbor]:
            return True

        # Otherwise check that letters match at overlapping indices
        else:
            iter = self.crossword.overlaps[var, neighbor]  # Their indices

            if iter:
                x, y = iter
                return var_value[x] == neighbor_value[y]

    def consistent(self, assignment: dict[Variable, str]):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        seen_values = set()

        for var, val in assignment.items():
            # If the assigned word is already used, not consistent:
            if val in seen_values:
                return False

            seen_values.add(val)

            # Var declared value length should match assigned val length
            if len(val) != var.length:
                return False

            # Check if there are conflicts between neighboring variables:
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    neighbor_val = assignment[neighbor]
                    # Check if neighbor variable is assigned and satisfies constraints
                    if not self.overlap_satisfied(var, neighbor, val, neighbor_val):
                        return False

        # Otherwise all assignments are consistent
        return True

    def order_domain_values(
        self, var: Variable, assignment: dict[Variable, str]
    ) -> list[str]:
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # amount of variables ruled if var takes this value
        ruleouts = {val: 0 for val in self.domains[var]}

        for val in self.domains[var]:
            for neighbor in self.crossword.neighbors(var):
                for neighbor_val in self.domains[neighbor]:
                    if not self.overlap_satisfied(var, neighbor, val, neighbor_val):
                        ruleouts[val] += 1

        return sorted(ruleouts.keys(), key=lambda val: ruleouts[val])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = set(self.domains.keys()) - set(assignment.keys())
        res = list(unassigned)
        res.sort(
            key=lambda x: (len(self.domains[x]), -len(self.crossword.neighbors(x)))
        )
        return res[0]

    def backtrack(self, assignment: dict[Variable, str]) -> dict[Variable, str] | None:
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        if self.assignment_complete(assignment):
            return assignment

        # look for unassigned vars
        var = self.select_unassigned_variable(assignment)

        for val in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = val

            if self.consistent(new_assignment):
                orig_domains = self.domains
                new_domains = deepcopy(self.domains)
                new_domains[var] = {val}

                # check if new domain is consistent
                self.domains = new_domains
                if not self.ac3():
                    continue

                solution = self.backtrack(new_assignment)
                if solution:
                    return solution

                # rolling back domains
                self.domains = orig_domains

        return None


def main():
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
