# Review documentation for human usefulness

Use this optional review when a page is technically detailed but readers still
cannot understand a flow, find an operation, or complete a task. The
[Documentation Reviewer](../../agents/documentation-reviewer.agent.md) provides
an independent reader perspective; the [quality skill](../../skills/documentation-quality-review/SKILL.md)
can also be used in ordinary Agent mode. Neither substitutes for source accuracy review.

## Install only what you need

No installer is required. Copy `agents/documentation-reviewer.agent.md` into
`.github/agents/`, any selected whole skill folders from `skills/` into
`.github/skills/`, and `prompts/review-documentation.prompt.md` into
`.github/prompts/` in your target project. Preserve filenames and supporting files.
Compare existing destinations and preserve project-owned customizations before replacing.
Each component can be installed independently.

With the [optional CLI](../../README.md#advanced-optional-cli), preview:

```sh
copilot-toolkit install project TARGET \
  --agents documentation-reviewer \
  --skills documentation-quality-review,diagram-review,rendered-docs-review \
  --prompts review-documentation \
  --dry-run
```

Replace `TARGET` with an existing project directory. Remove `--dry-run` after
reviewing the preview. Differing files are refused by default; compare and merge
customizations before considering explicit replacement with backups. To install
just the method, use `--skills documentation-quality-review` alone. Agents and
skills also support `install user --surface cli`; this prompt is project-only.
Starter and core remain unchanged.

Installation proves file placement, not native discovery, prompt invocation,
actual skill loading, or tool permissions. See [native format and client limits](../native-locations.md)
and [live smoke tests](../live-smoke-tests.md). The format follows official
[agent configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration),
[CLI skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills),
and [prompt files](https://code.visualstudio.com/docs/agent-customization/prompt-files)
(consulted 2026-10-28). `include-custom-instructions` follows the existing CLI
convention; other hosts may differ. Live behavior remains unverified here.

## Choose a review

For a fictional subsystem page, select Documentation Reviewer if available or
paste the task prompt into ordinary Agent mode:

> Review docs/queue-recovery.md for a maintainer unfamiliar with the job queue.
> Use documentation-quality-review if available. Can a reader explain the retry
> boundary, find the implementation entry point, and determine whether recovery
> instructions suffice? Review only the page and its linked docs. Return material
> findings and small fixes in chat; do not edit files or inspect application source.

For an MkDocs-style site:

> Review the documentation entry page, navigation, and three representative deep
> pages for new developers. Try to explain the job lifecycle, find the local setup
> procedure, and determine how to diagnose a stalled job. Use documentation-quality-review
> and, where relevant and available, diagram-review and rendered-docs-review.
> Use the permitted local site preview or screenshots for visual findings; disclose
> missing rendering or viewport access. Review read-only and return a few material
> findings with precise locations, task evidence, and small fixes.

A text-only review can assess diagram semantics but cannot establish rendering.
Use existing browsers/screenshots and build/link checks where available; these
components require no browser installation. An LLM simulation is a proxy: ask an
unfamiliar developer to attempt the same task when feasible.

## Fit review into authoring

A useful human-directed sequence is source investigation with Systems Investigator,
scoped writing with Documentation, then independent source review using existing
roles/tools alongside reader review with Documentation Reviewer. Source and reader
passes can run separately in parallel. After a human selects targeted revisions,
apply them in a separately authorized pass, run appropriate checks, and publish
through the project's usual workflow. No fixed agent pipeline is required.

Review substantive pages while writing. Review cross-site navigation and visual
quality after a substantial group of pages changes. Use diagram/site skills only
when those artifacts exist. Keep source-confirmed, inferred, runtime-confirmed,
and unresolved distinctions from the [source documentation workflow](undocumented-system-discovery.md);
a clear explanation or passing implementation test does not establish domain truth.

For a focused smoke test, install into an isolated synthetic project and start a
fresh session. Confirm reviewer discovery and skill-loading indicators where the
client provides them. Launch the prompt through the client's supported UI or paste
it as a disclosed fallback. Request a docs-only task; verify precise page references,
admission of absent answers, rendering limits, and no file changes. Record client
version and actual loading evidence separately from response quality. Use the
[manual usability evaluation](../../evals/documentation-usability.md) for a controlled comparison.
