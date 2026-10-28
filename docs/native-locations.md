# Native locations and compatibility

The catalog is the source of truth. Copy selected files into the target scope,
preserving names and skill directories. Compare existing files and back them up
before any replacement; copied content becomes user-owned.

| Content | Project destination | Personal CLI destination |
| --- | --- | --- |
| Agents | `.github/agents/<name>.agent.md` | `~/.copilot/agents/<name>.agent.md` |
| Skills | `.github/skills/<name>/SKILL.md` | `~/.copilot/skills/<name>/SKILL.md` |
| Prompts | `.github/prompts/<name>.prompt.md` | Use copy/paste fallback |
| Path instructions | `.github/instructions/<name>.instructions.md` | Select project scope for this library |
| Project scaffold | `AGENTS.md` | Not applicable |
| Shared baseline/preferences | Deliberately integrate with existing instructions | `~/.copilot/copilot-instructions.md` |

Here `~` means the user's home directory, including on Windows. CLI configuration
can change its home; resolve the active location before copying. Do not overwrite
a global instructions file just to add one preference. The optional overlay is
text to review and integrate, not a separately auto-loaded configuration file.

These paths follow GitHub's documentation for [CLI custom agents](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/invoke-custom-agents),
[skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills),
[CLI instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions),
and [prompt files](https://docs.github.com/en/copilot/concepts/prompting-and-context/prompt-files).
The project layout is for local clients; a GitLab remote does not enable
GitHub.com cloud-agent features.

## JetBrains

Start with repository-scoped files. Use the IDE's Copilot customization controls
for global instructions and check your plugin's supported locations. Do not
assume that it reads CLI personal folders. See [JetBrains instructions](https://docs.github.com/en/copilot/how-tos/copilot-in-your-ide/customize-copilot/configure-custom-instructions/add-repository-instructions-in-your-ide?tool=jetbrains)
and the [feature matrix](https://docs.github.com/en/copilot/reference/copilot-feature-matrix).
When a feature is unavailable, paste the selected prompt or skill into the chat;
this does not establish automatic discovery.

## Format decisions

Agents use `name`, `description`, and `include-custom-instructions: true`.
The last field opts custom CLI subagents into repository instructions; it is not
a universal IDE setting. The [CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#repository-custom-instructions-for-subagents)
also describes conditions that disable instruction loading. Agents explicitly
ask to read applicable project instructions rather than relying on textual
references to cause loading.

No agent pins a model or tool allowlist. This preserves the client's tool access;
read-only role instructions are behavioral expectations, not a sandbox. Consult
[agent configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
for host-specific fields and permissions.

Skills use the [Agent Skills format](https://agentskills.io/specification), with
a matching directory/name and required description. Prompts are plain Markdown;
they require no host-specific variable syntax. Path instructions use `applyTo`
globs and remain opt-in.

## Verification limits

Format references were consulted on 2026-10-28. This library has not been
live-tested in Copilot CLI or JetBrains; version-specific discovery remains
unverified. Static tests do not prove instruction loading or better model output.

To verify your environment, use a synthetic repository, record the client/plugin
version, confirm the agent appears, and ask it to read a known file. Inspect
instruction/skill loading indicators if available. Test a missing database
definition: the answer should identify the missing authority rather than invent
a formula. For JetBrains, record the IDE and harness as well as plugin version.
Keep these checks separate from installer or file-format validation.
