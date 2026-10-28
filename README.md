# Copilot Engineering Toolkit

Reusable engineering instructions, agents, skills, and project scaffolds for
GitHub Copilot CLI and JetBrains. Use them to understand unfamiliar code, scope
changes, preserve contracts, and design meaningful verification.

Use the library by manual copying or with the optional Python 3.11+ installer.
Installation and audit commands work offline without runtime dependencies.
No Python runtime is needed to use the Markdown files. This is an independent
project with no employer or GitHub sponsorship claimed.

## Install with a preview

From a local clone, install the CLI into your Python environment and preview
changes to an **existing** project directory (replace `/work/my-project`):

```sh
python -m pip install .
copilot-toolkit install project /work/my-project --profile core --dry-run
copilot-toolkit install project /work/my-project --profile core
copilot-toolkit init /work/my-project --template base --dry-run
copilot-toolkit audit project /work/my-project
```

Use a direct path without `..` segments, such as `/work/my-project` or
`C:\work\my-project`, in the examples above.
The core profile installs four agents and eight skills; it does not change
global preferences or `AGENTS.md`. Run `init` without `--dry-run` to create an
incomplete scaffold, then specialize it from repository evidence.

Package building may download build tooling. For a fully offline start, run
`python -B -m copilot_engineering_toolkit catalog` from the clone's `src/` directory;
replace `catalog` with any command below. Alternatively install a local wheel
using `python -m pip install --no-index --no-deps path/to/toolkit.whl` with its
actual filename. See [installer usage and safety](docs/installer.md) for user
installation, selection, backups, and exit codes.

## Start with one agent and skill

From a local clone, open `src/copilot_engineering_toolkit/catalog/` in your file
manager. In an existing target repository:

1. Copy `agents/systems-investigator.agent.md` into `.github/agents/`.
2. Copy the entire `skills/legacy-contract-analysis/` folder into `.github/skills/`.
3. Review any existing destination before copying; keep a backup and compare
   differences instead of replacing customized files. Create directories only
   inside the intended repository.
4. Open the target repository in Copilot CLI or your JetBrains IDE. Confirm the
   agent appears in the client's agent selector. Ask it to trace an output field
   in your code and use `legacy-contract-analysis` if available.

Verify a cited file and symbol yourself. An agent's assertion that it used a
skill is insufficient evidence of loading; inspect client indicators when
available. If discovery is unavailable, paste the relevant Markdown into chat.
See [native locations and compatibility](docs/native-locations.md) for scope and
version limitations. File-manager copying works on Windows, macOS, and Linux.

## Choose the guidance you need

All paths below are under the [canonical catalog](src/copilot_engineering_toolkit/catalog/).

| Content | Included | Use |
| --- | --- | --- |
| Core agents | Architect, Systems Investigator, Test Engineer, Documentation | Distinct analytical or writing roles |
| Core skills | Eight methods listed below | Available to ordinary Agent mode or specialists |
| Prompts | Analyze work item, bootstrap AGENTS, investigate behavior, review change | Launch a specific task |
| Templates | Base, .NET, Python, Go | Evidence-grounded project onboarding |
| Engineering baseline | `global/engineering.md` | Optional shared engineering expectations |
| Personal preferences | `global/preferences-optional.md` | Optional, editable communication style |
| Path instructions | C#, SQL, Python, Go | Opt-in language guidance |
| Project context | `instructions/project-context.md` | Optional small Copilot bridge to project-owned instructions |

The eight core skills are:

- `repository-onboarding`: map a repository and establish project instructions.
- `work-item-analysis`: turn a request into a bounded change and test approach.
- `change-impact-analysis`: trace consumers and regression risks.
- `test-design`: derive oracles and adversarial cases from contracts.
- `legacy-contract-analysis`: establish provenance and migration parity limits.
- `api-contract-evolution`: assess wire compatibility and migration order.
- `database-change-safety`: plan preservation, backfills, and recovery checks.
- `incident-triage`: distinguish causes and safe recovery options from evidence.

Core identifies the default agent/skill collection. Preferences, prompts, and
language rules are selected deliberately; nothing installs automatically.
No extended agents or skills are currently included.

For project onboarding, copy the chosen `templates/<name>/AGENTS.md.tmpl` as
`AGENTS.md` only if none exists; otherwise compare it with the existing file.
Supply `prompts/bootstrap-agents.prompt.md` to Copilot to specialize it from
repository evidence. Placeholders are not verified facts. The project owns the
resulting file and subsequent changes.

Use default Agent mode for implementation. Select a specialist when its role
helps; no fixed workflow or orchestration engine is required. Prompt boundaries
do not enforce filesystem permissions. Copilot discovery and behavior have not
been live-tested for this library.

## Development

Development uses Python 3.11+, uv, pytest, isort, Ruff, and Black. See
[contributing](CONTRIBUTING.md#development-commands) for setup, checks, and builds.
Tests cover catalog structure, installer safety, and static audit behavior, not
model behavior. Keep distributable content in the catalog without duplicate exports.

Licensed under [Apache-2.0](LICENSE). The library expresses the author's supplied
engineering requirements and reference principles in native Copilot formats.
It includes no employer source or private repository history. Examples are
fictional. Keep company-specific policies and project data in a separate private
derivative; manually review public updates before incorporating them there.
