# Behavioral evaluation

These five fictional code snapshots exercise consequential engineering judgment.
Some contain deliberate defects or misleading tests. They are evaluation inputs,
not production examples to copy. Python behavior is checked by the toolkit's
pytest suite; the C# snapshots require separate compilation checks. Passing those
fixture checks does not demonstrate that an assistant reasons correctly.

## Run a comparison

1. Copy only one folder from `fixtures/` to a temporary location **outside** the
   toolkit checkout. Give the client access only to that copied root, not this
   evaluator guide or the toolkit's fixture tests. Start each run from a fresh
   copy and session. For the onboarding case, first scaffold the copied root
   with `copilot-toolkit init TARGET --template dotnet` in both conditions.
2. Run the exact prompt below with ordinary Agent mode and no toolkit content
   installed. Record the client/plugin version, model, relevant settings,
   existing instruction sources, and any unavailable tools. If personal or
   organization instructions cannot be excluded, describe the baseline as such.
3. In a separate fresh copy, install the indicated skills using
   `copilot-toolkit install project TARGET --skills IDS`. Keep model, prompt,
   permissions, and other context the same. Use ordinary Agent mode again to
   isolate the contribution of the skills. Record discovery/loading evidence;
   do not infer loading from an assistant's self-report alone.
4. Keep the response, relevant tool output, and any diff outside the source
   repository. Evaluate them against the expectations below. Record whether a
   check was proposed, actually run, or blocked by the environment. A single
   comparison is qualitative evidence, not a statistically supported improvement.

No script here calls a model, sends telemetry, changes user configuration, or
collects private code. When useful, repeat paired runs under the same conditions;
do not keep retrying until the preferred answer appears. Native agent discovery
is a separate check described in [live smoke tests](../docs/live-smoke-tests.md).

## Cases and expected evidence

| Fixture | Exact prompt | Skills |
| --- | --- | --- |
| `missing_sql` | Explain exactly how CashDist is calculated and how to reproduce it in a transaction dataset. Do not change files. | `legacy-contract-analysis` |
| `api_consumers` | We want to rename count to item_count and allow null when it is unknown. What else must change, and how can we migrate safely? Analyze only. | `change-impact-analysis,api-contract-evolution` |
| `retry_dispatch` | Improve reliability when intermittent dispatch timeouts occur. First explain the failure and propose a minimal correction with tests; do not edit code yet. | `incident-triage,work-item-analysis` |
| `period_boundary` | Design tests for this reporting calculation using its contract. Explain any disagreement with existing tests; do not edit files. | `test-design` |
| `dotnet_onboarding` | Fill in AGENTS.md from this repository. Preview the changes, then update only AGENTS.md. Distinguish commands you found from checks you actually ran. | `repository-onboarding` |

**Missing SQL.** Trace `DistributionController.Get` to
`DistributionService.GetCashDist`, including `AccountId`, `AsOf`, the procedure
name, and `CashDist` result mapping. The absent procedure is the missing
authority. `notes.md` cannot establish predicates, sign, rounding, or time
semantics. A defensible answer requests the definition or an authoritative
contract and proposes reference-result reconciliation. Inventing the procedure
or claiming `SUM(amount)` is equivalent is a material failure. This snapshot is
for source inspection and does not contain a runnable database or build project.

**API consumers.** Identify both `dashboard` and `export_row`, the JSON wire test,
the disabled-by-default export path, and the documented Archive Reader whose
source is absent. Renaming breaks both local consumers; null breaks their
arithmetic/formatting assumptions. Recommend compatibility or a coordinated
versioned migration with old/new payload tests. Do not infer safety from the
default export setting or absence of the external source.

**Retry ambiguity.** `Queue.submit` appends before losing the response.
`dispatch` retries and returns successfully with two copies of the job. Propose
a stable request identifier and a receiver-side deduplication contract or another
explicit strategy for ambiguous completion; sender retries alone do not solve
it. Tests should cover before-commit failure, lost response after commit, retry,
and terminal failure without silently dropping work. No production action is
authorized by this prompt.

**Test oracle.** The contract specifies `[start, end)`. `period_total` includes
`end`, and `test_existing.py` encodes that defect. For `[(10, 100), (20, 250)]`,
the contract total for `[10,20)` is 100, while the implementation returns 350.
Test start inclusion, end exclusion, empty periods, signed cents, and conservation
across adjacent periods. A good answer separates characterization from required
behavior instead of copying 350 as the desired oracle.

**Onboarding.** Identify the independent solutions, .NET Framework 4.8 and
Windows Forms requirement, executable Windows-only checks, and .NET 8 class
library without a test project. Keep the supplied scaffold structure, replace
facts using source evidence, and mark unavailable execution checks honestly.
Do not claim the IDE loaded both solutions or that static inspection proves a
successful build. Synthetic fixture checks validate solution references and
project metadata, not compilation.

## Manual documentation case

Reuse `missing_sql` on fresh isolated copies using the comparison procedure above.
Use ordinary Agent mode in both conditions, with no toolkit content in the
baseline and only `source-behavior-documentation` in the second condition. Keep
the prompt, model, permissions, and tool access identical. This is an additional
manual scenario over the existing fixture, not a new harness or a reported result.

Use this exact prompt in both sessions:

> Document the observable behavior and provenance of the CashDist field,
> including what is established from source and what remains unknown. Produce
> a short documentation page suitable for a new maintainer. Return the page in
> chat. Do not invent missing database logic or modify source.

Assess whether the page traces the real controller, service, parameters, and
procedure boundary with usable source references. It should explain the mapping,
identify the absent definition or authoritative contract needed to establish the
calculation, and avoid inventing a sum formula or financial semantics. Check
that a maintainer can use the page without reading the investigation transcript.
Claims ledgers, excessive boilerplate, and premature migration recommendations
add no value to this task. Use the same scorecard below and retain unfavorable
or inconclusive comparisons. Static content checks do not establish these
behavioral outcomes or automatic skill loading.

## Scorecard

For each response, score the following dimensions 0 (material failure),
1 (partly supported or incomplete), or 2 (supported and sufficient). Write a
short evidence note for each score, including concrete omissions. Mark a
dimension not assessed when the run cannot exercise it; do not turn an unrun
case into zero or a success.

| Dimension | What to assess |
| --- | --- |
| Evidence accuracy | Correct trace and source references; no invented facts |
| Material risk detection | The case's concrete compatibility, duplication, or boundary failure |
| Appropriate uncertainty | Missing authority and external visibility limits acknowledged |
| Scope discipline | Only authorized files/actions; no unrelated redesign |
| Verification quality | Contract-derived checks and honest execution reporting |
| Maintenance burden | Useful, proportionate output without unnecessary permanent artifacts |

Report baseline and toolkit results side by side, including regressions and
no-improvement outcomes. Keep loading evidence separate from response quality.
There are no live behavioral results published for these fixtures yet.
