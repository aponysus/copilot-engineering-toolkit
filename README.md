# Copilot Engineering Toolkit

Reusable engineering instructions, agents, skills, and project templates for
GitHub Copilot CLI and JetBrains. Start by copying one agent and one skill into
an existing project. **No Python or installer is required.**

## Quick start: copy one agent and skill

Download or clone this repository. Open the
[content catalog](src/copilot_engineering_toolkit/catalog/) in your file manager.
Copy these two items into your target project's root, creating folders as needed:

| Copy from the catalog | Destination in your project |
| --- | --- |
| [agents/systems-investigator.agent.md](src/copilot_engineering_toolkit/catalog/agents/systems-investigator.agent.md) | `.github/agents/systems-investigator.agent.md` |
| [skills/change-impact-analysis/](src/copilot_engineering_toolkit/catalog/skills/change-impact-analysis/) — the whole folder | `.github/skills/change-impact-analysis/` |

Keep the skill's `SKILL.md` filename and any supporting files. If a destination
already exists, compare it and keep a backup before replacing customized content.

Open the target project in Rider, another supported JetBrains IDE, or GitHub
Copilot CLI. Look for **Systems Investigator** in the agent selector. Select it
and ask, substituting a real symbol from your project:

> Read the source for `<symbol>` and use change-impact-analysis to identify its
> callers and compatibility risks. Cite file locations. Do not edit files.

Check one cited symbol against the source. Inspect the client's skill-loading
indicator when available; an assistant's claim alone does not prove loading.
If discovery is unavailable, paste the selected Markdown into chat and treat
that as a fallback, not native discovery. See [native locations](docs/native-locations.md)
and the [Rider smoke check](docs/live-smoke-tests.md#rider-and-other-jetbrains-ides)
for version-specific checks. This workflow works through file copying on Windows,
macOS, and Linux; live client support remains unverified for this library.

## Project setup: the recommended starter

Add [work-item-analysis](src/copilot_engineering_toolkit/catalog/skills/work-item-analysis/)
to the quick start by copying that entire folder into `.github/skills/`.
The starter is now one agent and two skills:

- **Systems Investigator** traces actual behavior and missing dependencies.
- **Work Item Analysis** turns a request into a bounded change and test approach.
- **Change Impact Analysis** identifies affected consumers and regression risks.

For project context, choose a [base](src/copilot_engineering_toolkit/catalog/templates/base/AGENTS.md.tmpl),
[.NET](src/copilot_engineering_toolkit/catalog/templates/dotnet/AGENTS.md.tmpl),
[Python](src/copilot_engineering_toolkit/catalog/templates/python/AGENTS.md.tmpl), or
[Go](src/copilot_engineering_toolkit/catalog/templates/go/AGENTS.md.tmpl) scaffold.
Copy it as `AGENTS.md` only if the project has none; otherwise compare it with
existing instructions. Use the [bootstrap prompt](src/copilot_engineering_toolkit/catalog/prompts/bootstrap-agents.prompt.md)
to fill it from repository evidence. Placeholders are not verified facts.
The resulting instructions belong to the project and are never synchronized.

For Copilot-specific context, optionally copy
[project-context.md](src/copilot_engineering_toolkit/catalog/instructions/project-context.md)
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
The full collection is available with explicit `--profile core`, or by manually
copying the four agent files and eight skill folders linked below.

## Browse the collection

Keep only the capabilities useful to your project. Ordinary Agent mode handles
implementation; specialist roles do not require a fixed sequence of steps.

| Content | Canonical files |
| --- | --- |
| Agents | [Architect](src/copilot_engineering_toolkit/catalog/agents/architect.agent.md), [Systems Investigator](src/copilot_engineering_toolkit/catalog/agents/systems-investigator.agent.md), [Test Engineer](src/copilot_engineering_toolkit/catalog/agents/test-engineer.agent.md), [Documentation](src/copilot_engineering_toolkit/catalog/agents/documentation.agent.md) |
| Prompts | [Four task launchers](src/copilot_engineering_toolkit/catalog/prompts/) |
| Shared guidance | [Engineering baseline](src/copilot_engineering_toolkit/catalog/global/engineering.md), [optional personal preferences](src/copilot_engineering_toolkit/catalog/global/preferences-optional.md) |
| Language instructions | [Opt-in C#, SQL, Python, and Go guidance](src/copilot_engineering_toolkit/catalog/instructions/) |

All eight core skills remain available:

- [Repository onboarding](src/copilot_engineering_toolkit/catalog/skills/repository-onboarding/)
- [Work-item analysis](src/copilot_engineering_toolkit/catalog/skills/work-item-analysis/)
- [Change-impact analysis](src/copilot_engineering_toolkit/catalog/skills/change-impact-analysis/)
- [Test design](src/copilot_engineering_toolkit/catalog/skills/test-design/)
- [Legacy contract analysis](src/copilot_engineering_toolkit/catalog/skills/legacy-contract-analysis/)
- [API contract evolution](src/copilot_engineering_toolkit/catalog/skills/api-contract-evolution/)
- [Database change safety](src/copilot_engineering_toolkit/catalog/skills/database-change-safety/)
- [Incident triage](src/copilot_engineering_toolkit/catalog/skills/incident-triage/)

The catalog stays in one canonical location so manual copies and packaged
installations use the same content. No extended agents or skills are included.

## Advanced: optional CLI

For repeated installations, the CLI offers component selection, preview diffs,
conflict refusal, backups, and read-only audits. It requires Python 3.11+.
From a clone, install it in your chosen Python environment:

```sh
python -m pip install .
copilot-toolkit install project /work/my-project --agents systems-investigator --skills change-impact-analysis --dry-run
```

No selection flags means the three-component **starter**, not the full collection.
Global preferences, prompts, and language rules require explicit selection.
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
