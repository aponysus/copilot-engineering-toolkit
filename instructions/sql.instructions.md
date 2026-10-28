---
applyTo: "**/*.sql"
---

# SQL

Establish the database engine/version, migration conventions, and observable contract. Preserve parameter types, result shape, grain, null behavior, time boundaries, sign, units/currency, and rounding order where relevant. Parameterize untrusted values; do not concatenate them into executable SQL.

Check join multiplicity, predicates, transaction boundaries, lock behavior, and old/new application compatibility. Use actual plans and representative evidence before asserting performance improvements. Counts alone do not prove reconciliation.

Use isolated synthetic data for checks. State migration/backfill preconditions, recovery limits, and validation. Never run production-changing or destructive SQL without explicit authorization for the target and action; a script's existence does not grant permission.
