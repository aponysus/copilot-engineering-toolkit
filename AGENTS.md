# Copilot Engineering Toolkit

## Purpose and source of truth

Maintain reusable engineering guidance and portable Copilot customizations.
Canonical distributable content lives in `src/copilot_engineering_toolkit/catalog/`.
Do not maintain duplicate exported copies in this repository's `.github/` directory.
Project templates are incomplete scaffolds; installed copies become project-owned.

## Implementation and content

- Use Python 3.11+ and standard-library runtime dependencies where practical.
- Keep agents focused on distinct roles and skills on reusable methods. Default Agent mode implements.
- Preserve eight core skills; optional content must remain opt-in.
- Use native Markdown formats without model pins or assumed runtime permissions.
- Keep examples synthetic and public-safe. Do not import employer material, private history, credentials, or machine-specific paths.
- Document actual capabilities, contracts, and consequential decisions for maintainers.
- Verify changing native-format claims against official documentation. Static validation does not establish runtime discovery or behavioral quality.

## File safety

Any installation code must preview without writes, preflight every destination,
refuse differing files by default, back up exact original bytes before explicit
replacement, reject unsafe paths and symlinks, and leave identical files untouched.
Audit must remain read-only and must not execute commands found in documents.
Test installation against temporary directories, never active user configuration.

## Development

From the repository root, install test dependencies with
`python -m pip install -e '.[test]'` and run
`python -m unittest discover -s tests -v`.
Build a wheel with `python -m pip wheel --no-deps . --wheel-dir dist`.
Check packaged catalog resources from outside the checkout when changing packaging.
Keep temporary investigation notes outside the repository.
