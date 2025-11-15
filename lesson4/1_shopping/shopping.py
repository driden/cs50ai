import csv
import sys


from numpy.lib import npyio
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

import numpy as np
from numpy.typing import NDArray

from typing import Any, Sequence

TEST_SIZE = 0.4
RETURNING_VISITOR = "Returning_Visitor"
TRUE = "TRUE"
MODEL = KNeighborsClassifier(n_neighbors=1)


def main():
    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename) -> tuple[list[Any], list[Any]]:
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    evidences: list[Sequence[float]] = []
    labels: list[int] = []

    with open(filename) as csvfile:
        lines = csv.DictReader(csvfile)
        for line in lines:
            evidence, label = parse_line(line)
            evidences.append(evidence)
            labels.append(label)

    return evidences, labels


MONTHS = {
    "Jan": 0,
    "Feb": 1,
    "Mar": 2,
    "Apr": 3,
    "May": 4,
    "June": 5,
    "Jul": 6,
    "Aug": 7,
    "Sep": 8,
    "Oct": 9,
    "Nov": 10,
    "Dec": 11,
}


def parse_month(month: str) -> int:
    """
    Parses month string, returns an ordinal
    """
    return MONTHS[month]


def parse_visitor_type(visitorType: str) -> int:
    """
    Parses visitor type
    Returns
     - 0 for "not returning"
     - 1 for "returning"
    """

    return 1 if visitorType == RETURNING_VISITOR else 0


def parse_boolean(boolean: str) -> int:
    """
    Parses Weekend
    Returns
     - 0 for "FALSE"
     - 1 for "TRUE"
    """
    return 1 if boolean == TRUE else 0


def parse_evidence(line: dict[str | Any, str | Any]) -> Sequence[float]:
    """
    Parses the evidences fields and converts them to their respective float/int representations
    """
    res: list[float] = []
    res.append(int(line["Administrative"]))
    res.append(float(line["Administrative_Duration"]))
    res.append(int(line["Informational"]))
    res.append(float(line["Informational_Duration"]))
    res.append(int(line["ProductRelated"]))
    res.append(float(line["ProductRelated_Duration"]))
    res.append(float(line["BounceRates"]))
    res.append(float(line["ExitRates"]))
    res.append(float(line["PageValues"]))
    res.append(float(line["SpecialDay"]))
    res.append(parse_month(line["Month"]))
    # - OperatingSystems, an integer
    res.append(int(line["OperatingSystems"]))
    # - Browser, an integer
    res.append(int(line["Browser"]))
    # - Region, an integer
    res.append(int(line["Region"]))
    # - TrafficType, an integer
    res.append(int(line["TrafficType"]))
    # - VisitorType, an integer 0 (not returning) or 1 (returning)
    res.append(parse_visitor_type(line["VisitorType"]))
    # - Weekend, an integer 0 (if false) or 1 (if true)
    res.append(parse_boolean(line["Weekend"]))

    return res


def parse_label(line: dict[str | Any, str | Any]) -> int:
    return parse_boolean(line["Revenue"])


def parse_line(line: dict[str | Any, str | Any]) -> tuple[Sequence[float], int]:
    """
    Given a CSV line it parses the evidence to be only numeric values and the label
    """
    evidence = parse_evidence(line)
    label = parse_label(line)

    return evidence, label


def train_model(
    evidence: list[Sequence[float]], labels: list[int]
) -> KNeighborsClassifier:
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model


def evaluate(
    labels: list[int], predictions: NDArray[np.float64]
) -> tuple[float, float]:
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    true_positives = 0
    true_negatives = 0

    for i in range(len(labels)):
        label = labels[i]
        prediction = predictions[i]

        if label == 1 and prediction == 1:
            true_positives += 1
        elif label == 0 and prediction == 0:
            true_negatives += 1

    positives = sum([1 if label == 1 else 0 for label in labels])
    negatives = sum([1 if label == 0 else 0 for label in labels])

    return true_positives / positives, true_negatives / negatives


if __name__ == "__main__":
    main()
