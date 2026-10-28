# Copilot Engineering Toolkit

Reusable engineering instructions, agents, skills, and project scaffolds for
GitHub Copilot CLI and JetBrains. Use them to understand unfamiliar code, scope
changes, preserve contracts, and design meaningful verification.

The library is usable by manual copying. An installer and audit CLI are not yet
available. No Python runtime is needed to use the Markdown files. This is an
independent project with no employer or GitHub sponsorship claimed.

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

Python 3.11+ is required for package development. In an isolated environment:

```sh
python -m pip install -e '.[test]'
python -m unittest discover -s tests -v
python -m pip wheel --no-deps . --wheel-dir dist
```

Tests check content structure and packaged resources, not model behavior.
Keep all distributable content in the catalog; do not add duplicate exports.
See [contributing](CONTRIBUTING.md) for content conventions.

Licensed under [Apache-2.0](LICENSE). The library expresses the author's supplied
engineering requirements and reference principles in native Copilot formats.
It includes no employer source or private repository history. Examples are
fictional. Keep company-specific policies and project data in a separate private
derivative; manually review public updates before incorporating them there.
