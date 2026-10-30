"""Summarize fictional account line items in integer cents."""

from collections.abc import Callable


class SummaryCache:
    def __init__(self, calculate: Callable[[tuple[int, ...]], int] = sum) -> None:
        self.calculate = calculate
        self.cache: dict[str, int] = {}

    def total(self, account: str, items: tuple[int, ...]) -> int:
        if account not in self.cache:
            self.cache[account] = self.calculate(items)
        return self.cache[account]
