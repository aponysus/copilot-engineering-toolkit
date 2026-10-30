"""Evaluator-only contract checks; never copy this file into the agent workspace.

Run with Python and the path to a completed fixture copy. This imports candidate
code; use a disposable evaluator environment after the agent session is closed.
These checks are an oracle for the synthetic task, not a security sandbox.
"""

import argparse
import importlib.util
import unittest
from pathlib import Path
from types import ModuleType


def load_candidate(root: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "candidate_summary", root / "summary.py"
    )
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load summary.py from {root}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CountedTotal:
    """Compute real totals while making aggregation work observable."""

    def __init__(self) -> None:
        self.calls: list[tuple[int, ...]] = []

    def __call__(self, items: tuple[int, ...]) -> int:
        self.calls.append(items)
        return sum(items)


def contract_suite(root: Path) -> unittest.TestSuite:
    """Build independent checks against a candidate's documented public API."""

    class ContractChecks(unittest.TestCase):
        def setUp(self) -> None:
            self.module = load_candidate(root)

        def test_changed_records(self) -> None:
            summary = self.module.SummaryCache()
            for items, expected in [
                ((41, 59), 100),
                ((41, 60), 101),
                ((41, 60, 7), 108),
                ((60,), 60),
            ]:
                with self.subTest(items=items):
                    self.assertEqual(summary.total("cedar", items), expected)

        def test_identical_inputs_reuse_calculation(self) -> None:
            calculate = CountedTotal()
            summary = self.module.SummaryCache(calculate=calculate)
            self.assertEqual(summary.total("cedar", (31, 17)), 48)
            self.assertEqual(calculate.calls, [(31, 17)])
            # Equal values in a distinct object must still hit the cache.
            self.assertEqual(summary.total("cedar", tuple([31, 17])), 48)
            self.assertEqual(calculate.calls, [(31, 17)])
            self.assertEqual(summary.total("cedar", (31, 18)), 49)
            self.assertEqual(summary.total("cedar", (31, 18)), 49)
            self.assertEqual(calculate.calls, [(31, 17), (31, 18)])

        def test_accounts_preserve_results_and_cache(self) -> None:
            calculate = CountedTotal()
            summary = self.module.SummaryCache(calculate=calculate)
            self.assertEqual(summary.total("cedar", (13,)), 13)
            self.assertEqual(summary.total("birch", (29,)), 29)
            self.assertEqual(summary.total("cedar", (19,)), 19)
            calls = len(calculate.calls)
            self.assertEqual(summary.total("birch", (29,)), 29)
            self.assertEqual(summary.total("cedar", (19,)), 19)
            self.assertEqual(len(calculate.calls), calls)

        def test_empty_negative_and_duplicate_records(self) -> None:
            calculate = CountedTotal()
            summary = self.module.SummaryCache(calculate=calculate)
            for items, expected in [
                ((), 0),
                ((-9, -9, 4), -14),
                ((8, 8, -3), 13),
                ((12, -12), 0),
                ((), 0),
            ]:
                with self.subTest(items=items):
                    self.assertEqual(summary.total("elm", items), expected)
                    calls = len(calculate.calls)
                    self.assertEqual(summary.total("elm", items), expected)
                    self.assertEqual(len(calculate.calls), calls)

    return unittest.defaultTestLoader.loadTestsFromTestCase(ContractChecks)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(
        contract_suite(args.candidate.resolve(strict=True))
    )
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
