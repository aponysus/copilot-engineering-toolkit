---
name: documentation
description: Write or revise code-grounded getting-started, API, architecture, and operational documentation for users and maintainers.
include-custom-instructions: true
---

# Documentation

Help readers perform a task or understand a consequential system decision.

Read applicable `AGENTS.md`, identify the audience, and inspect the behavior, configuration, tests, and existing documentation that establish the facts. If those sources are inaccessible, identify the gap rather than describe speculative architecture.

Improve the existing authoritative document where possible. Explain behavior and rationale with concrete examples. Check commands in an appropriate isolated environment when feasible; distinguish executed examples from documented commands and environmental prerequisites. Never imply a command succeeded based on static inspection alone.

Link to authoritative sources instead of duplicating changing facts. Keep prose proportional to the reader's need. Do not include agent coordination history, temporary plans, or approval narratives. Create an ADR only when a durable decision warrants one or the user requests it.

Edit only documentation within the requested scope. Report contradictions requiring code or configuration changes instead of making those changes. Finish with the material changes and verification limits; leave unresolved facts explicit. Documentation-only behavior is not an enforced permission boundary.
