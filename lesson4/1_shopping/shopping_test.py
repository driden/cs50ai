import pytest

from shopping import parse_evidence, parse_line

lines_test_data = [
    (
        {
            "Administrative": "0",
            "Administrative_Duration": "0",
            "Informational": "0",
            "Informational_Duration": "0",
            "ProductRelated": "1",
            "ProductRelated_Duration": "0",
            "BounceRates": "0.2",
            "ExitRates": "0.2",
            "PageValues": "0",
            "SpecialDay": "0",
            "Month": "Feb",
            "OperatingSystems": "1",
            "Browser": "1",
            "Region": "1",
            "TrafficType": "1",
            "VisitorType": "Returning_Visitor",
            "Weekend": "FALSE",
            "Revenue": "FALSE",
        },
        [
            0,
            0,
            0,
            0,
            1,
            0,
            0.2,
            0.2,
            0,
            0,
            1,
            1,
            1,
            1,
            1,
            1,
            0,
        ],
    ),
    (
        {
            "Administrative": "0",
            "Administrative_Duration": "0",
            "Informational": "0",
            "Informational_Duration": "0",
            "ProductRelated": "19",
            "ProductRelated_Duration": "154.2166667",
            "BounceRates": "0.015789474",
            "ExitRates": "0.024561404",
            "PageValues": "0",
            "SpecialDay": "0",
            "Month": "Feb",
            "OperatingSystems": "2",
            "Browser": "2",
            "Region": "1",
            "TrafficType": "3",
            "VisitorType": "Returning_Visitor",
            "Weekend": "FALSE",
        },
        [
            0,
            0,
            0,
            0,
            19,
            154.2166667,
            0.015789474,
            0.024561404,
            0,
            0,
            1,
            2,
            2,
            1,
            3,
            1,
            0,
        ],
    ),
]


@pytest.mark.parametrize("input,expected", lines_test_data)
def test_parse_evidence(input, expected):
    res = parse_evidence(input)
    assert expected == res
