---
applyTo: "**/*.cs"
---

# C#

Inspect project target frameworks, language versions, nullable settings, and local conventions before using newer syntax or APIs. Distinguish .NET Framework and Windows-only dependencies from cross-platform .NET; do not assume every solution builds in the current environment.

Preserve public APIs, serialized names, and exception behavior. Follow established async and cancellation patterns, propagate cancellation where supported, and account for disposal and partial failure. Do not introduce sync-over-async or dependencies to simplify a small change without a concrete reason.

Trace SQL/procedure boundaries when results depend on them; missing definitions limit conclusions. Run the relevant solution/test project with its required toolchain and report environmental limits. Do not upgrade frameworks or packages without task scope.
