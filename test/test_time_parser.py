
import pytest

from utils.time_parser import timestamp_to_seconds


@pytest.mark.parametrize(
    "timestamp, expected",
    [
        ("[00:12.50]", 12.5),
        ("[01:25.30]", 85.3),
        ("[03:10.00]", 190.0),
        ("[00:45]", 45.0),
        ("[02:15.5]", 135.5),
        ("[02:15.05]", 135.05),
        ("[02:15.005]", 135.005),
    ],
)
def test_timestamp_to_seconds(timestamp, expected):
    assert timestamp_to_seconds(timestamp) == pytest.approx(expected)


@pytest.mark.parametrize(
    "timestamp",
    [
        "00:12.50",
        "[00:60.50]",
        "[-01:20.00]",
        "[abc]",
        "[01:20.1234]",
        "",
    ],
)
def test_invalid_timestamp(timestamp):
    with pytest.raises(ValueError):
        timestamp_to_seconds(timestamp)
