"""Existing aggregation regression check."""

from totals import period_total


def test_report_total() -> None:
    assert period_total([(10, 100), (20, 250)], 10, 20) == 350
