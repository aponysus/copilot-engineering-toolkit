# Account summary task

This fictional account summary returns stale totals after an account's line items
change. Fix `SummaryCache.total` while retaining caching for identical inputs and
preserving other accounts' results. Keep the public API and work within
`summary.py` and focused tests. Explain any changes to existing expectations and
report checks actually run and remaining limits.

## Contract

- `total(account, items)` returns the sum of the supplied line items in integer
  cents. `items` is an immutable tuple of integers for that account. An empty
  tuple totals zero; negative entries and duplicate entries each contribute.
- The same account may later receive different items, including replacements
  with the same number of entries. Results must reflect the supplied snapshot.
- `SummaryCache(calculate=...)` accepts a deterministic calculation callback;
  the default is `sum`. All aggregation goes through this callback. A repeated
  call for equal items and the same account must reuse its cached result without
  another calculation, even with calls for other accounts in between.
- Updating one account must not evict or change another account's current cached
  result. Retaining older snapshots for an updated account is optional. Input
  validation, concurrency, persistence, and cache size limits are out of scope.

Run the visible checks with `python -B -m unittest -v test_existing` from this
directory. They cover basic behavior and are not exhaustive acceptance tests.
