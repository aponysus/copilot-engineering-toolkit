# Manual documentation-usability comparison

Lantern Jobs is fictional. Copy only `fixtures/documentation_usability/` outside
this checkout for each run; expose only that copied root. It intentionally contains
incomplete Markdown documentation, no application source, renderer, or executable
commands. Keep this prompt and the evaluation key below outside the accessible root.
No behavioral results have been collected; static tests preserve inputs, not judgment.

Run ordinary Agent mode on a fresh copy/session without toolkit content. On another
fresh copy/session install Documentation Reviewer and the three review skills,
then select the reviewer if supported. Use the same model, exact prompt below,
files, tools, and permissions as far as practical; the selected customization is
the intended difference. If isolating the skill alone, use ordinary Agent mode in
both conditions and install only documentation-quality-review in the second.
Record unavoidable differences and inherited instructions. Never provide the key.

> Review the Lantern Jobs docs for a new developer and a maintainer. Read-only;
> use documentation only. Attempt these reader tasks: explain the job lifecycle
> and how eligible work is determined; find how to pause intake and its implementation
> entry point; determine the exact safe recovery steps for a stuck job; identify
> the maximum retry count before a job is abandoned; assess whether the processing
> diagram helps explain the lifecycle. Record paths and supported answers or gaps,
> then give a few material findings with precise locations and smallest useful fixes.
> Distinguish diagram semantics from visual observations. Do not change files.

Record client/plugin versions, model/settings, instructions, native loading evidence,
response, tools/permissions, actual source access (expected none), and checks actually
performed versus suggested. Keep outputs outside the repository. Compare evidence
for comprehension, findability, workflow sufficiency, uncertainty, diagram review,
and scope discipline using the [existing scorecard](README.md#scorecard), or mark
dimensions not assessed. Record regressions and no improvement as well as gains.
Rendering/keyboard/responsive quality is not assessed without actual render access;
if supplied, give both conditions identical artifacts and tools. No browser install
or model API runner is required. A simulation does not prove human onboarding gains.

## Evaluator key — never copy into the fixture root

- **Comprehension:** `docs/index.md` → Processing supports intake, ready queue,
  worker lease, record writing, acknowledgment, and expired-lease requeue.
  `processing.md` gives a formula without defining checkpoint, effective window,
  or stride/units. Eligible work cannot be meaningfully calculated; request
  definitions and a worked example without inventing semantics.
- **Findability:** index → Notes → Detail 7 contains pause/resume syntax and
  `src/intake/control.py::pause_queue`. A direct search may succeed; report that
  actual path rather than invent a navigation failure. The labels hide the operation
  from navigation. Relabel the entry/heading to expose intake control. Do not claim
  to inspect the implementation or execute the command.
- **Action:** Troubleshooting gives no inspection command, safety criterion,
  recovery tool name/settings, or log location. Exact safe recovery steps cannot
  be performed from these docs. Ask for those details instead of supplying commands.
- **Unknown:** no maximum retry count or abandonment policy is supplied anywhere.
  Admitting absence is required; guessing a conventional count is a material failure.
- **Diagram:** `processing.md` routes lease expiry from Completed to Ready queue,
  while prose assigns leases to claimed jobs and says acknowledgment completes them.
  Flag the contradicted relationship and suggest representing worker lease expiry
  separately from successful completion, subject to source confirmation. Source
  truth is unavailable. Mermaid text does not prove clipping, clutter, or rendering.

Prioritize consequential gaps over cosmetic edits. A good review separates reader
obstacles from suspected factual inconsistency, gives evidence and small fixes,
and leaves files unchanged. The key is qualitative guidance, not a required prose
snapshot or evidence of measured superiority over ordinary Agent mode.
