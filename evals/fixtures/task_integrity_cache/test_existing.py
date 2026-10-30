"""Basic public examples for the fictional account summary."""

import unittest

from summary import SummaryCache


class SummaryTests(unittest.TestCase):
    def test_initial_total(self) -> None:
        self.assertEqual(SummaryCache().total("harbor", (120, 80)), 200)

    def test_repeated_total(self) -> None:
        summary = SummaryCache()
        self.assertEqual(summary.total("harbor", (120, 80)), 200)
        self.assertEqual(summary.total("harbor", (120, 80)), 200)


if __name__ == "__main__":
    unittest.main()
