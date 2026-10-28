# Copilot Engineering Toolkit

## Purpose and source of truth

Maintain reusable engineering guidance and portable Copilot customizations.
Canonical distributable content lives in the root `agents/`, `skills/`, `prompts/`,
`instructions/`, `templates/`, and `global/` folders, indexed by `manifest.json`.
Wheel builds bundle generated copies as package resources; never edit those copies.
Do not maintain duplicate exported copies in this repository's `.github/` directory.
Project templates are incomplete scaffolds; installed copies become project-owned.

## Implementation and content

- Use Python 3.11+ and standard-library runtime dependencies where practical.
- Use uv for this repository's dependencies and environment, pytest for tests,
  isort for import sorting, Ruff for linting, and Black for formatting. These
  development choices do not impose tools on consuming projects.
- Use type hints throughout Python code, built-in generic types, and Google-style
  docstrings where behavior or interfaces need explanation.
- Prefer the smallest coherent change; inspect code and tests, preserve local
  conventions, and avoid unrelated refactors or speculative abstractions.
- Keep agents focused on distinct roles and skills on reusable methods. Default Agent mode implements.
- Preserve eight core skills; optional content must remain opt-in.
- Use native Markdown formats without model pins or assumed runtime permissions.
- Keep examples synthetic and public-safe. Do not import employer material, private history, credentials, or machine-specific paths.
- Document actual capabilities, contracts, and consequential decisions for maintainers.
- Keep each enduring fact in one authoritative place. Exclude agent coordination,
  review history, and internal approval narratives from maintained documentation;
  preserve actual domain-level operational authorization constraints.
- Treat this file as a stable contract. Preserve its headings and order, and change
  it only for enduring requirements with explicit user authorization. Report
  proposed instruction changes discovered during ordinary work instead of applying them.
- Verify changing native-format claims against official documentation. Static validation does not establish runtime discovery or behavioral quality.

## File safety

Any installation code must preview without writes, preflight every destination,
refuse differing files by default, back up exact original bytes before explicit
replacement, reject unsafe paths and symlinks, and leave identical files untouched.
Audit must remain read-only and must not execute commands found in documents.
Test installation against temporary directories, never active user configuration.

## Development

Use the reusable commands in [CONTRIBUTING.md](CONTRIBUTING.md) from the repository root.
Run checks proportional to changed behavior and risk; report observed outcomes
and material limits. Avoid tests that merely mirror implementation details.
Check packaged catalog resources from outside the checkout when changing packaging.
Use a configured external workspace for transient plans and notes, or the
conversation if none is available. Keep durable specifications and decisions in
the repository; do not classify existing plans as transient by their path alone.
