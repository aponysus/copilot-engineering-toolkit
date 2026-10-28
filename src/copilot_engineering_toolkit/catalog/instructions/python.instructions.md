---
applyTo: "**/*.py"
---

# Python

Follow the project's supported Python versions, packaging, type conventions, and import layout. Use the repository's dependency manager, test runner, formatter, and lint configuration; do not impose a new toolchain.

Avoid import-time I/O in libraries. Preserve public signatures, exceptions, serialization, and compatibility expectations. Make resource cleanup and async cancellation explicit where relevant; do not hide operational failures with broad exception handling.

Use deterministic fixtures and isolated environments for behavior checks. Distinguish working from the checkout from working as an installed package. Keep dependency and interpreter upgrades within the requested scope.
