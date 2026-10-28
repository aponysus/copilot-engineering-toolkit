"""Existing API regression checks."""

from service import response


def test_count_wire_representation() -> None:
    assert response(2) == '{"count": 2}'
