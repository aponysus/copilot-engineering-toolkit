# Understand and document an unfamiliar system

Start with one subsystem and one useful question. A source map helps you choose
an execution path to investigate; tracing that path gives you enough evidence
to write a useful page. Repeat as needed. A large speculative overview is harder
to trust and maintain than a small explanation whose claims lead to exact code.

You can begin with source access alone. Runtime experiments come later, when a
reference environment and authorization are available. Systems Investigator,
Documentation, and Test Engineer offer useful specializations, but ordinary
Agent mode can use the same skills and prompts. Nothing schedules or delegates
these tasks automatically.

## Copy the source investigation tools

From a clone of this toolkit, copy the following into an existing target project.
Paths on the right are relative to that project's root. Create missing folders;
compare and back up customized files before replacing them. No Python is needed.

| Copy from this toolkit | Destination in the target project |
| --- | --- |
| [agents/systems-investigator.agent.md](../../agents/systems-investigator.agent.md) | `.github/agents/systems-investigator.agent.md` |
| [agents/documentation.agent.md](../../agents/documentation.agent.md) | `.github/agents/documentation.agent.md` |
| [skills/source-behavior-documentation/](../../skills/source-behavior-documentation/) — whole folder | `.github/skills/source-behavior-documentation/` |
| [skills/legacy-contract-analysis/](../../skills/legacy-contract-analysis/) — optional, whole folder | `.github/skills/legacy-contract-analysis/` |
| [prompts/map-undocumented-system.prompt.md](../../prompts/map-undocumented-system.prompt.md) | `.github/prompts/map-undocumented-system.prompt.md` |
| [prompts/document-subsystem.prompt.md](../../prompts/document-subsystem.prompt.md) | `.github/prompts/document-subsystem.prompt.md` |

Keep each skill's `SKILL.md` and supporting resources together. Open the target
project in your client and check agent and skill discovery. If prompt-file
invocation is unavailable, paste the prompt text into chat. If skills are not
discovered, provide their text explicitly and record that as a fallback;
an assistant's self-report does not prove native loading. See
[native locations](../native-locations.md) and [live checks](../live-smoke-tests.md).

For an existing CLI installation, the same selection is available after reading
the [installer guide](../installer.md). Replace `TARGET` with the direct path to
your existing project, quoting paths containing spaces:

```sh
copilot-toolkit install project TARGET --agents systems-investigator,documentation --skills source-behavior-documentation,legacy-contract-analysis --prompts map-undocumented-system,document-subsystem --dry-run
```

Review the diff, then remove `--dry-run` to install. This does not create or
rewrite `AGENTS.md`. The new skills and prompts are optional extended content;
neither the default starter nor the core profile includes them.

## Map first, then follow one path

1. Select Systems Investigator or ordinary Agent mode. Invoke
   `map-undocumented-system` and supply a bounded target, for example:
   “Map the distribution-response subsystem from source only. Identify its
   entry points, dependencies, tests, and missing authority. Keep findings in
   chat; do not edit files.” Confirm source access and the revision inspected.
2. Use the map to choose a representative vertical slice: one request to its
   returned field, one scheduled job to its persisted output, or one UI action
   to its underlying service. Prefer a path that resolves an important question
   without requiring an exhaustive codebase survey.
3. Trace that slice through callers, models, orchestration, queries, state, and
   consumers. Use `legacy-contract-analysis` for detailed calculation or SQL
   provenance. A procedure call can establish inputs and mappings even when its
   implementation is missing; stop claims about its calculation at that boundary.
4. Select Documentation or ordinary Agent mode and invoke `document-subsystem`.
   Supply the slice, findings, and permitted documentation path. For example:
   “Document the distribution-response slice in the existing subsystem guide.
   Verify important claims against source. Edit only that documentation.”
   Prior findings are navigation aids; source remains necessary evidence.
5. Check consequential claims in a separate source-review pass or session. The
   existing Architect or ordinary code review can help; no new reviewer agent
   is needed. Follow references, check missing branches, and challenge any
   formula or deployment assertion not supported by the inspected evidence.
6. Repeat for the next useful slice, updating the same maintained documentation.
   Keep temporary investigation notes in chat or approved scratch storage rather
   than adding competing reports to the target repository.

The [source-behavior-documentation skill](../../skills/source-behavior-documentation/SKILL.md)
contains the full investigation method and evidence rules. Source investigation
and documentation requests do not authorize production-code changes or rewriting
project instructions.

## Write pages a maintainer can use

Reuse the project's existing documentation layout and site conventions. Start
with one coherent page and link it from an existing entry point. Split it only
when readers need separate navigation: architecture/responsibilities, an
execution lifecycle, domain entities, database contracts, or individual
calculations. Add a verification section or page only when there is substantive
evidence to record. Do not generate a directory of empty placeholders or use
`AGENTS.md` as the system's architecture manual.

A calculation reference can cover these questions, omitting irrelevant ones:

| Topic | Useful content |
| --- | --- |
| Entry point and purpose | Operation, responsible component, and source symbols |
| Inputs | Identity, row/aggregation grain, time basis and boundaries, units/currency |
| Derivation | Confirmed computation and rounding order, or the retrieval boundary where authority is missing |
| Dependencies | Queries, procedures, configuration, cached state, and prior runs |
| Output | Shape, consumers, persistence, sign/null/default behavior |
| Edge and failure behavior | Empty inputs, branches, partial completion, rerun/restart constraints |
| Evidence and unknowns | Baseline revision, relative source paths and symbols, actual observations, missing definitions |

For example, the fictional [missing SQL fixture](../../evals/fixtures/missing_sql/)
supports a short page tracing `DistributionController.Get` to
`DistributionService.GetCashDist`, the `AccountId` and `AsOf` parameters passed
to `sp_GetDistributions`, and the returned `CashDist` mapping. It does not
establish a sum formula or financial interpretation. Explain that distinction
and identify the missing procedure definition or authoritative contract.

Use relative links and source symbols that readers can follow; line numbers can
supplement them. State the baseline revision and any relevant uncommitted changes.
A small Mermaid flow or mathematical expression is useful only when its
relationships or derivation are supported. Write the behavior and rationale,
not a transcript of the investigation.

## Keep evidence types distinct

| Label | What it establishes |
| --- | --- |
| Source-confirmed | Inspected implementation or authoritative contract at an identified revision; name the authority |
| Inferred | A plausible, explicitly limited interpretation awaiting evidence |
| Runtime-confirmed | An actual observation for specified version, configuration, state, and inputs |
| Unresolved | Missing or contradictory evidence and what would settle it |

Use these distinctions where they change the reader's understanding, without
labeling every sentence. Checked-in source does not establish which binary or
configuration is deployed. Matching a reference output establishes limited
behavioral parity; independent domain correctness requires its own authority.
Existing behavior, including behavior encoded in tests, can be defective.

## Add runtime experiments when useful

For this later step, copy the entire
[runtime-characterization](../../skills/runtime-characterization/) and
[test-design](../../skills/test-design/) folders into `.github/skills/`, and
[characterize-runtime.prompt.md](../../prompts/characterize-runtime.prompt.md)
into `.github/prompts/`. Test Engineer is an optional role; ordinary Agent mode
is sufficient. The separate CLI selection is:

```sh
copilot-toolkit install project TARGET --skills runtime-characterization,test-design --prompts characterize-runtime --dry-run
```

Review the preview and remove `--dry-run` to install. Invoke the prompt with the
uncertain behavior, competing hypotheses, reference environment, and permitted
execution scope. Without live access, ask for an experiment design. This does
not require a desktop driver, data-export tool, or new test harness.

Choose a case whose possible results distinguish the hypotheses. For example,
two synthetic events at a reporting window's endpoints can distinguish an
inclusive end from an exclusive end; an event strictly inside cannot. Record
the reference build, configuration, data/schema snapshot, frozen inputs, prior
state, predicted outputs, and comparison rules before execution. Specify allowed
side effects, reset/recovery conditions, and where evidence may be retained.

Only execute within explicit authorization for that environment and action.
Do not submit real jobs, modify production data, or probe sensitive systems on
the strength of a prompt. Prefer synthetic or approved non-sensitive fixtures.
For actual runs, associate outputs, logs, warnings/errors, and run outcomes with
their environment and run identity. Compare against source expectations and
prior runs using justified rules for decimals, order, time, and tolerances.

Update the affected page with supported observations and contradictions, keeping
runtime confirmation scoped to tested conditions. Where practical and authorized,
turn stable reference cases into executable characterization tests. Do not relax
tolerances to hide mismatches or treat replication of a defect as domain correctness.
The [runtime-characterization skill](../../skills/runtime-characterization/SKILL.md)
provides the full method and stopping rules.

## Client, repository, and data boundaries

Copying local files into a GitLab-hosted checkout does not enable GitHub.com
cloud-agent functionality. Test discovery in the actual client/version you use.
An editor may display a full directory without semantically loading every
solution; choose the relevant solution and prerequisites explicitly. Source
search is not proof of a successful build, and the checkout may differ from
running binaries. Keep these limits explicit when interpreting results.

This toolkit and its examples are employer-neutral. Corporate source, findings,
and runtime evidence belong only in approved internal project locations. Do not
upstream company-specific notes, source excerpts, data, or screenshots to this
toolkit or send them through unapproved tools.

A useful stopping point is a page a new engineer can follow to exact code,
understand what is established, and identify the next evidence needed. One
well-supported slice is useful before every calculation is understood. Stop an
experiment when it resolves the question, yields an honestly inconclusive
result, or requires a new access/data decision.

For a separate reader-experience pass after authoring, use the optional
[documentation-quality review](documentation-quality-review.md). It complements
source review with documentation-only reader tasks.
