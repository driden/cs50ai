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


def main():
    # fam = {
    #     "Harry": {"name": "Harry", "mother": "Lily", "father": "James", "trait": None},
    #     "James": {"name": "James", "mother": None, "father": None, "trait": None},
    #     "Lily": {"name": "Lily", "mother": None, "father": None, "trait": None},
    # }
    # joint_probability(fam, set(), set(), set())

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {"gene": {2: 0, 1: 0, 0: 0}, "trait": {True: 0, False: 0}}
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):
        # Check if current set of people violates known information
        fails_evidence = any(
            (
                people[person]["trait"] is not None
                and people[person]["trait"] != (person in have_trait)
            )
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):
                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


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


# Probabilties of inheriting 1 gene
inherit_gen_prob = {0: PROBS["mutation"], 1: 0.5, 2: 1 - PROBS["mutation"]}


# Probabilites of inheriting a specific `gene_countz
def gene_count_inherit(gene_count, father_prob, mother_prob):
    match gene_count:
        # Both parents give you one gene
        case 2:
            return mother_prob * father_prob
        # Only one of your parents gives a gene
        case 1:
            return (1 - mother_prob) * father_prob + mother_prob * (1 - father_prob)
        # No parents give a gene
        case 0:
            return (1 - mother_prob) * (1 - father_prob)
    assert (False, "Shouldn't get here")  # noqa: F631
    return 0  # should not happen


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
        mother = people[person]["mother"]
        father = people[person]["father"]

        if mother is None or father is None:
            gene_prob = PROBS["gene"][gene_count]

        else:
            prob_mother = inherit_gen_prob[
                person_gene_count(mother, one_gene, two_genes)
            ]
            prob_father = inherit_gen_prob[
                person_gene_count(father, one_gene, two_genes)
            ]
            gene_prob = gene_count_inherit(gene_count, prob_father, prob_mother)

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

    for person in probabilities:
        gene_count = person_gene_count(person, one_gene, two_genes)

        probabilities[person]["gene"][gene_count] = (
            probabilities[person]["gene"][gene_count] + p
        )
        probabilities[person]["trait"][person in have_trait] = (
            probabilities[person]["trait"][person in have_trait] + p
        )


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        # {2: 0.1, 1: 0.3, 0: 0.1}
        # 0.1 x + 0.3x + 0.1X = 1
        # 0.8x = 1
        # x = 1 / 0.5
        # x = 2

        probabilities[person]["gene"] = {
            key: value * 1 / sum(probabilities[person]["gene"].values())
            for (key, value) in probabilities[person]["gene"].items()
        }

        probabilities[person]["trait"] = {
            key: value * 1 / sum(probabilities[person]["trait"].values())
            for (key, value) in probabilities[person]["trait"].items()
        }


if __name__ == "__main__":
    main()
