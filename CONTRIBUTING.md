# Contributing

Edit canonical content in `src/copilot_engineering_toolkit/catalog/`. Agents
define distinct roles; skills define reusable methods; prompts launch tasks;
templates contain conspicuous placeholders. Avoid duplicating whole methods
inside agents or broad policies inside every file.

Register each component in `catalog/manifest.json` with its type-qualified ID,
tier, canonical source, and permitted destinations. Core-profile selection covers
core agents and skills only; other content requires explicit selection. Keep
installation mappings declarative so adding a skill needs no installer change.
Skill folders may contain supporting resources; the installer copies them as a
unit. Runtime code uses the standard library; PyYAML is a test dependency only.

A useful skill has a discriminating description, evidence to inspect, a method
that changes decisions, a proportional output, and a stopping condition for
missing authority. Keep it usable without a particular specialist or connector.
Examples must be independently fictional and public-safe.

Use native frontmatter, preserve canonical identifiers, and check format changes
against official documentation. Do not pin models or imply Markdown enforces
permissions. A template must not assert commands or runtime facts about an
uninspected repository.

## Development commands

Use Python 3.11+ and uv. The checked-in `uv.lock` fixes development dependency
versions; `uv sync --locked` creates or updates the local `.venv`.

```sh
uv sync --locked
uv run --locked pytest
uv run --locked ruff check .
uv run --locked isort --check-only src tests
uv run --locked black --check src tests
uv build
```

To apply import sorting and formatting, run `uv run --locked isort src tests`
followed by `uv run --locked black src tests`. isort uses Black's compatibility
profile. Ruff handles linting and annotations; Black handles formatting, and
isort owns import order. Update dependencies deliberately with uv and include the
resulting lockfile changes.

Use type hints throughout Python code, preferring built-in generic types such
as `list[str]`. Use Google-style docstrings to explain non-obvious interfaces,
side effects, and failure behavior; avoid docstrings that merely repeat a name.
Write new tests with pytest. Existing unittest-based cases run under pytest and
can be adapted when substantive test changes warrant it.

Keep changes coherent and scoped. Run checks appropriate to the affected
contracts and failure modes, and expand verification only for material risk or
unresolved evidence. Report actual results and update affected user documentation.
For packaging changes, build and
install the wheel into an isolated environment, change outside the checkout,
and verify catalog files through `importlib.resources`. Model behavior and native
client discovery need separate live checks; report unperformed checks plainly.

Write for users and maintainers, explaining behavior and consequential tradeoffs.
Use existing authoritative documents rather than duplicate facts. Keep temporary
plans, agent coordination, and review history out of project documentation.
Preserve genuine operational authorization semantics. Before finishing prose,
read it as someone unfamiliar with the development conversation and remove
process narration or artifacts that add maintenance without helping the reader.

Do not submit private project code, logs, tickets, internal policies, or credentials.
Keep company-specific derivatives separate and review any generic contribution
for public suitability. Do not add mandatory services, telemetry, background
synchronization, or process documents without a concrete user need.
