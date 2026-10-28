# Distribution endpoint

The endpoint accepts an account and an as-of timestamp and returns `CashDist`.
Database procedure definitions are maintained separately from this source snapshot.

An old implementation note says: “CashDist is SUM(amount).” The note gives no
procedure version, filtering rules, or comparison results.
