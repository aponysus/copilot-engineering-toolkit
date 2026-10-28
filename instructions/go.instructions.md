---
applyTo: "**/*.go"
---

# Go

Follow the module's Go version, package boundaries, error conventions, and gofmt formatting. Preserve exported API and wire compatibility. Introduce interfaces only when they serve a concrete consumer or testing boundary.

Propagate `context.Context` through operations that support cancellation. Define goroutine ownership, termination, channel ownership, and resource cleanup. Avoid unbounded work, swallowed errors, and retries without an idempotency argument.

Use deterministic synchronization in concurrency tests. Run focused tests and the race detector when relevant and supported; distinguish tool/platform limits from passing results. Do not change modules or upgrade the toolchain outside scope.
