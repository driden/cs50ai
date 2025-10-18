import csv
import itertools
import sys

PROBS = {
    # Unconditional probabilities for having gene
    "gene": {2: 0.01, 1: 0.03, 0: 0.96},
    "trait": {
        # Probability of trait given two copies of gene
        2: {True: 0.65, False: 0.35},
        # Probability of trait given one copy of gene
        1: {True: 0.56, False: 0.44},
        # Probability of trait given no gene
        0: {True: 0.01, False: 0.99},
    },
    # Mutation probability
    "mutation": 0.01,
}


# trait = false, gene_count = 0
## James
#  pJ = 0.96 (gene) * 0.99 (trait)
#  pL = 0.96 (gene) * 0.99 (trait)
#  pH = 0.01 * 0.96 + 0.01 * 0.96

# total =


def main():
    fam = {
        "Harry": {"name": "Harry", "mother": "Lily", "father": "James", "trait": None},
        "James": {"name": "James", "mother": None, "father": None, "trait": None},
        "Lily": {"name": "Lily", "mother": None, "father": None, "trait": None},
    }
    joint_probability(fam, set(), set(), set())
    # Check for proper usage
    # if len(sys.argv) != 2:
    #     sys.exit("Usage: python heredity.py data.csv")
    # people = load_data(sys.argv[1])
    #
    # # Keep track of gene and trait probabilities for each person
    # probabilities = {
    #     person: {"gene": {2: 0, 1: 0, 0: 0}, "trait": {True: 0, False: 0}}
    #     for person in people
    # }
    #
    # # Loop over all sets of people who might have the trait
    # names = set(people)
    # for have_trait in powerset(names):
    #     # Check if current set of people violates known information
    #     fails_evidence = any(
    #         (
    #             people[person]["trait"] is not None
    #             and people[person]["trait"] != (person in have_trait)
    #         )
    #         for person in names
    #     )
    #     if fails_evidence:
    #         continue
    #
    #     # Loop over all sets of people who might have the gene
    #     for one_gene in powerset(names):
    #         for two_genes in powerset(names - one_gene):
    #             # Update probabilities with new joint probability
    #             p = joint_probability(people, one_gene, two_genes, have_trait)
    #             update(probabilities, one_gene, two_genes, have_trait, p)
    #
    # # Ensure probabilities sum to 1
    # normalize(probabilities)
    #
    # # Print results
    # for person in people:
    #     print(f"{person}:")
    #     for field in probabilities[person]:
    #         print(f"  {field.capitalize()}:")
    #         for value in probabilities[person][field]:
    #             p = probabilities[person][field][value]
    #             print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (
                    True
                    if row["trait"] == "1"
                    else False
                    if row["trait"] == "0"
                    else None
                ),
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s)
        for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def person_gene_count(person, one_gene, two_genes):
    if person in one_gene:
        return 1
    if person in two_genes:
        return 2
    return 0


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    prob = 1
    for person in people:
        gene_count = person_gene_count(person, one_gene, two_genes)

        if people[person]["mother"] is None or people[person]["father"] is None:
            gene_prob = PROBS["gene"][gene_count]

        else:
            # If a parent has two copies of the mutated gene, then they will pass the mutated gene on to the child;
            # if a parent has no copies of the mutated gene, then they will not pass the mutated gene on
            # to the child; and if a parent has one copy of the mutated gene, then the gene is passed on to the child
            # with probability 0.5. After a gene is passed on, though, it has some probability of undergoing
            # additional mutation: changing from a version of the gene that causes hearing impairment to a
            # version that doesn’t, or vice versa.
            gcm = person_gene_count(people[person]["mother"], one_gene, two_genes)

            if gcm == 0:
                prob_mother_giving_gen = PROBS["mutation"]
            elif gcm == 1:
                prob_mother_giving_gen = 0.5
            else:
                prob_mother_giving_gen = 1 - PROBS["mutation"]

            p_M = prob_mother_giving_gen

            gcf = person_gene_count(people[person]["father"], one_gene, two_genes)

            if gcf == 0:
                prob_father_giving_gen = PROBS["mutation"]
            elif gcf == 1:
                prob_father_giving_gen = 0.5
            else:
                prob_father_giving_gen = 1 - PROBS["mutation"]

            p_F = prob_father_giving_gen

            match gene_count:
                # Both parents give you one gene
                case 2:
                    gene_prob = p_M * p_F
                # Only one of your parents gives a gene
                case 1:
                    gene_prob = (1 - p_M) * p_F + p_M * (1 - p_F)
                # No parents give a gene
                case 0:
                    gene_prob = (1 - p_M) * (1 - p_F)

        # prob of having `gene_count` and `have_trait`
        prob *= gene_prob * PROBS["trait"][gene_count][person in have_trait]

    return prob


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    raise NotImplementedError


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
