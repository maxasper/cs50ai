import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():
    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
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
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


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
    p = 1
    for person_name in people:
        person = people[person_name]
        is_has_trait_check = person_name in have_trait
        has_parents = person['mother'] is not None
        genes_count = 1 if person_name in one_gene else 2 if person_name in two_genes else 0
        if has_parents:
            mother_name = person['mother']
            father_name = person['father']
            mother_gene_count = 1 if mother_name in one_gene else 2 if mother_name in two_genes else 0
            father_gene_count = 1 if father_name in one_gene else 2 if father_name in two_genes else 0
            p_genes_from_mother = abs(mother_gene_count * 0.5 - 0.01)
            p_genes_from_father = abs(father_gene_count * 0.5 - 0.01)
            p_no_genes_from_mother = 1 - p_genes_from_mother
            p_no_genes_from_father = 1 - p_genes_from_father

            if genes_count == 0:
                current_genes_count_probability = p_no_genes_from_mother * p_no_genes_from_father
            elif genes_count == 1:
                current_genes_count_probability = (p_genes_from_mother * p_no_genes_from_mother +
                                                   p_genes_from_father * p_no_genes_from_mother)
            else:
                current_genes_count_probability = p_genes_from_mother * p_genes_from_father

            p *= (current_genes_count_probability * PROBS["trait"][genes_count][is_has_trait_check])
        else:
            p *= (PROBS["gene"][genes_count] * PROBS["trait"][genes_count][is_has_trait_check])
    return p


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        data = probabilities[person]
        if person in have_trait:
            data["trait"][True] += p
        else:
            data["trait"][False] += p

        if person in one_gene:
            data["gene"][1] += p
        elif person in two_genes:
            data["gene"][2] += p
        else:
            data["gene"][0] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        data_trait = probabilities[person]['trait']
        trait_sum = sum(data_trait.values())
        if trait_sum != 0:
            data_trait[True] = data_trait[True] / trait_sum
            data_trait[False] = data_trait[False] / trait_sum

        data_gene = probabilities[person]['gene']
        data_gene_sum = sum(data_gene.values())
        if data_gene_sum != 0:
            for i in data_gene:
                data_gene[i] = data_gene[i] / data_gene_sum


if __name__ == "__main__":
    main()
