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

Run the README's test command after changes. For packaging changes, build and
install the wheel into an isolated environment, change outside the checkout,
and verify catalog files through `importlib.resources`. Model behavior and native
client discovery need separate live checks; report unperformed checks plainly.

Do not submit private project code, logs, tickets, internal policies, or credentials.
Keep company-specific derivatives separate and review any generic contribution
for public suitability. Do not add mandatory services, telemetry, background
synchronization, or process documents without a concrete user need.
