# Copilot Engineering Toolkit

Reusable engineering instructions, agents, skills, and project templates for
GitHub Copilot. Start by copying one agent and one skill into
an existing project. **No Python or installer is required.**

## Quick start: copy one agent and skill

Download or clone this repository. Open its top-level [agents/](agents/) and
[skills/](skills/) folders in your file manager.
Copy these two items into your target project's root, creating folders as needed:

| Copy from the catalog | Destination in your project |
| --- | --- |
| [agents/systems-investigator.agent.md](agents/systems-investigator.agent.md) | `.github/agents/systems-investigator.agent.md` |
| [skills/change-impact-analysis/](skills/change-impact-analysis/) — the whole folder | `.github/skills/change-impact-analysis/` |

Keep the skill's `SKILL.md` filename and any supporting files. If a destination
already exists, compare it and keep a backup before replacing customized content.

Open the target project in your editor's Copilot chat or GitHub Copilot CLI.
If your client supports custom agents, look for **Systems Investigator** in the agent selector. Select it
and ask, substituting a real symbol from your project:

> Read the source for `<symbol>` and use change-impact-analysis to identify its
> callers and compatibility risks. Cite file locations. Do not edit files.

Check one cited symbol against the source. Inspect the client's skill-loading
indicator when available; an assistant's claim alone does not prove loading.
If discovery is unavailable, paste the selected Markdown into chat and treat
that as a fallback, not native discovery. See [native locations](docs/native-locations.md)
and the [editor smoke check](docs/live-smoke-tests.md#editor-integration)
for client-specific checks. This workflow works through file copying on Windows,
macOS, and Linux; live client support remains unverified for this library.

## Project setup: the recommended starter

Add [work-item-analysis](skills/work-item-analysis/)
to the quick start by copying that entire folder into `.github/skills/`.
The starter is now one agent and two skills:

- **Systems Investigator** traces actual behavior and missing dependencies.
- **Work Item Analysis** turns a request into a bounded change and test approach.
- **Change Impact Analysis** identifies affected consumers and regression risks.

For project context, choose a [base](templates/base/AGENTS.md.tmpl),
[.NET](templates/dotnet/AGENTS.md.tmpl),
[Python](templates/python/AGENTS.md.tmpl), or
[Go](templates/go/AGENTS.md.tmpl) scaffold.
Copy it as `AGENTS.md` only if the project has none; otherwise compare it with
existing instructions. Use the [bootstrap prompt](prompts/bootstrap-agents.prompt.md)
to fill it from repository evidence. Placeholders are not verified facts.
The resulting instructions belong to the project and are never synchronized.

The Python and Go templates include opinionated tooling, environment, and
verification defaults. Python uses uv, pytest, isort, Ruff, and Black; Go favors
the standard toolchain, a standard-library-first core, and explicit module checks.
Review these defaults against an existing project's conventions. Templates create
instructions only; follow their setup guidance to configure the actual tools.

For Copilot-specific context, optionally copy
[project-context.md](instructions/project-context.md)
as `.github/copilot-instructions.md`. Compare with existing rules first.
This small bridge asks the agent to read project instructions; verify actual
loading in your client rather than assuming the reference causes it.

If you already use the optional CLI, the equivalent starter installation is:

```sh
copilot-toolkit install project /work/my-project --profile starter --dry-run
copilot-toolkit install project /work/my-project --profile starter
copilot-toolkit init /work/my-project --template dotnet --dry-run
```

Replace the target with your existing project directory, for example
`"C:\work\my-project"` on Windows. `init` is separate: remove `--dry-run` only when
you want to create the scaffold. Component installation does not rewrite `AGENTS.md`.
The core collection is available with explicit `--profile core`, or by manually
copying the four agent files and eight skill folders linked below.

## Browse the collection

Keep only the capabilities useful to your project. Ordinary Agent mode handles
implementation; specialist roles do not require a fixed sequence of steps.

| Content | Canonical files |
| --- | --- |
| Agents | [Architect](agents/architect.agent.md), [Systems Investigator](agents/systems-investigator.agent.md), [Test Engineer](agents/test-engineer.agent.md), [Documentation](agents/documentation.agent.md) |
| Prompts | [Reusable task launchers](prompts/) |
| Shared guidance | [Engineering baseline](global/engineering.md), [optional personal preferences](global/preferences-optional.md) |
| Language instructions | [Opt-in C#, SQL, Python, and Go guidance](instructions/) |

All eight core skills remain available:

- [Repository onboarding](skills/repository-onboarding/)
- [Work-item analysis](skills/work-item-analysis/)
- [Change-impact analysis](skills/change-impact-analysis/)
- [Test design](skills/test-design/)
- [Legacy contract analysis](skills/legacy-contract-analysis/)
- [API contract evolution](skills/api-contract-evolution/)
- [Database change safety](skills/database-change-safety/)
- [Incident triage](skills/incident-triage/)

These top-level folders are the canonical content. Package builds bundle them
automatically, so manual copies and CLI installations use the same files.

## Optional: document an unfamiliar system

The [undocumented-system workflow](docs/workflows/undocumented-system-discovery.md)
walks through scoped source reconnaissance, writing maintainable documentation,
and later controlled runtime experiments. It uses the existing agents with
[source-behavior-documentation](skills/source-behavior-documentation/SKILL.md) and
[runtime-characterization](skills/runtime-characterization/SKILL.md), plus the
[map](prompts/map-undocumented-system.prompt.md),
[document](prompts/document-subsystem.prompt.md), and
[characterize](prompts/characterize-runtime.prompt.md) task prompts.
Manual copying is sufficient. These extended components require explicit
selection and are not included in starter or core.

## Optional: review documentation quality

Use the [documentation-quality workflow](docs/workflows/documentation-quality-review.md)
for independent reader review with [Documentation Reviewer](agents/documentation-reviewer.agent.md),
[documentation-quality-review](skills/documentation-quality-review/SKILL.md),
[diagram-review](skills/diagram-review/SKILL.md),
[rendered-docs-review](skills/rendered-docs-review/SKILL.md), and the
[review prompt](prompts/review-documentation.prompt.md). These five extended
components are individually opt-in; starter and core are unchanged.

## Advanced: optional CLI

For repeated installations, the CLI offers component selection, preview diffs,
conflict refusal, backups, and read-only audits. It requires Python 3.11+.
From the clone's root, install it as an isolated tool with
[uv](https://docs.astral.sh/uv/guides/tools/):

```sh
uv tool install .
copilot-toolkit install project /work/my-project --agents systems-investigator --skills change-impact-analysis --dry-run
```

If the command is not on your `PATH`, run `uv tool update-shell` and restart your
shell. To run directly from the checkout instead, use
`uv run --locked copilot-toolkit` followed by any command below, for example:

```sh
uv run --locked copilot-toolkit catalog
```

`uv run` manages the project's environment and installs the package automatically;
no separate package installation or `pip` module is needed. If you prefer pip,
`python -m pip install .` remains supported in an environment that includes pip.

No selection flags means the three-component **starter**, not the full collection.
Global preferences, prompts, and language rules require explicit selection.
To install only the engineering baseline and optional personal preferences for
GitHub Copilot CLI:

```sh
copilot-toolkit install user --surface cli --global engineering,preferences-optional --dry-run
copilot-toolkit install user --surface cli --global engineering,preferences-optional
```

This writes `~/.copilot/copilot-instructions.md` by default, without installing
agents or skills. `COPILOT_HOME` or an explicit path override changes the location.
Use `--global engineering` for the baseline alone. Editors may use different
global instruction locations; the CLI destination does not configure every editor.
See [installer usage](docs/installer.md) for global installation, updates, audits,
and safety limits. Native Windows/macOS filesystem checks remain unverified;
manual setup is the recommended starting point on those platforms.

Installation and audit commands work offline without runtime dependencies.
Package building may download build tools. For offline use from a clone, run
`python -B -m copilot_engineering_toolkit catalog` from `src/`, substituting another
command as needed. A local wheel can also be installed with
`python -m pip install --no-index --no-deps path/to/toolkit.whl` using its actual name.

## Development and validation

Development uses Python 3.11+, uv, pytest, isort, Ruff, and Black. See
[contributing](CONTRIBUTING.md#development-commands) for setup, checks, and builds.
[Live client checks](docs/live-smoke-tests.md) establish discovery and loading;
[synthetic evaluations](evals/README.md) exercise engineering judgment separately.
Static tests do not prove either. Prompt boundaries are not enforced permissions.

This independent project is licensed under [Apache-2.0](LICENSE), with no
employer or GitHub sponsorship claimed. Examples are fictional and public-safe.
Keep company-specific guidance in a separate private derivative and review
upstream changes before importing them. Local Copilot file discovery in a GitLab
checkout does not imply support for GitHub-hosted cloud-agent features.
