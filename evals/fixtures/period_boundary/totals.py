"""Aggregate synthetic events represented as (timestamp, amount_cents)."""


def period_total(events: list[tuple[int, int]], start: int, end: int) -> int:
    return sum(amount for timestamp, amount in events if start <= timestamp <= end)
