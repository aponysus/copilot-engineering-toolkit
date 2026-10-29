"""Validate the distributable native content, including installed resources."""

import unittest
from collections.abc import Iterator
from importlib.resources.abc import Traversable

import yaml

from copilot_engineering_toolkit.catalog import TYPES, Catalog
from copilot_engineering_toolkit.resources import catalog_root

CATALOG = catalog_root()
CORE_SKILLS = {
    "repository-onboarding",
    "work-item-analysis",
    "change-impact-analysis",
    "test-design",
    "legacy-contract-analysis",
    "api-contract-evolution",
    "database-change-safety",
    "incident-triage",
}
CORE_AGENTS = {"architect", "systems-investigator", "test-engineer", "documentation"}
EXTENDED_AGENTS = {"documentation-reviewer"}
EXTENDED_SKILLS = {
    "source-behavior-documentation",
    "runtime-characterization",
    "documentation-quality-review",
    "diagram-review",
    "rendered-docs-review",
}
CORE_PROMPTS = {
    "analyze-work-item",
    "bootstrap-agents",
    "investigate-behavior",
    "review-change",
}
EXTENDED_PROMPTS = {
    "map-undocumented-system",
    "document-subsystem",
    "characterize-runtime",
    "review-documentation",
}


def frontmatter(resource: Traversable) -> tuple[dict[str, object], str]:
    text = resource.read_text(encoding="utf-8")
    opening, metadata, body = text.split("---", 2)
    if opening or not body.strip():
        raise ValueError(f"Missing frontmatter or body: {resource.name}")
    data = yaml.safe_load(metadata)
    if not isinstance(data, dict):
        raise ValueError(f"Frontmatter must be a mapping: {resource.name}")
    return data, body


def descendants(resource: Traversable) -> Iterator[Traversable]:
    for child in resource.iterdir():
        if child.is_dir():
            yield from descendants(child)
        else:
            yield child


class ContentTests(unittest.TestCase):
    def test_all_core_and_extended_skills_have_valid_native_metadata(self) -> None:
        skills = list(CATALOG.joinpath("skills").iterdir())
        self.assertEqual({item.name for item in skills}, CORE_SKILLS | EXTENDED_SKILLS)
        catalog = Catalog()
        self.assertEqual(
            {c.id: c.tier for c in catalog.components if c.type == "skills"},
            dict.fromkeys(CORE_SKILLS, "core")
            | dict.fromkeys(EXTENDED_SKILLS, "extended"),
        )
        for folder in skills:
            with self.subTest(skill=folder.name):
                data, _ = frontmatter(folder.joinpath("SKILL.md"))
                self.assertEqual(data["name"], folder.name)
                self.assertRegex(data["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
                self.assertLessEqual(len(data["name"]), 64)
                self.assertIsInstance(data["description"], str)
                self.assertTrue(data["description"].strip())
                self.assertLessEqual(len(data["description"]), 1024)

    def test_core_agents_preserve_repository_context_without_model_or_tool_pins(
        self,
    ) -> None:
        agents = list(CATALOG.joinpath("agents").iterdir())
        self.assertEqual(
            {a.name for a in agents},
            {f"{a}.agent.md" for a in CORE_AGENTS | EXTENDED_AGENTS},
        )
        for agent in agents:
            with self.subTest(agent=agent.name):
                data, _ = frontmatter(agent)
                self.assertEqual(agent.name, f'{data["name"]}.agent.md')
                self.assertIsInstance(data["description"], str)
                self.assertTrue(data["description"].strip())
                self.assertIs(data["include-custom-instructions"], True)
                self.assertNotIn("model", data)
                self.assertNotIn("tools", data)

    def test_language_rules_have_intended_scope(self) -> None:
        # Each shipped glob intentionally covers one language at root and below.
        for language, extension in {
            "csharp": "cs",
            "sql": "sql",
            "python": "py",
            "go": "go",
        }.items():
            with self.subTest(language=language):
                data, _ = frontmatter(
                    CATALOG.joinpath("instructions", f"{language}.instructions.md")
                )
                self.assertEqual(data["applyTo"], f"**/*.{extension}")

    def test_templates_are_explicitly_incomplete(self) -> None:
        templates = list(CATALOG.joinpath("templates").iterdir())
        self.assertEqual(
            {t.name for t in templates}, {"base", "dotnet", "python", "go"}
        )
        for folder in templates:
            with self.subTest(template=folder.name):
                text = folder.joinpath("AGENTS.md.tmpl").read_text(encoding="utf-8")
                self.assertIn("{{PROJECT_NAME}}", text)
                self.assertIn("{{TEST_COMMAND}}", text)
                self.assertEqual(text.count("{{"), text.count("}}"))

    def test_task_prompts_are_packaged(self) -> None:
        expected = CORE_PROMPTS | EXTENDED_PROMPTS
        self.assertEqual(
            {c.id: c.tier for c in Catalog().components if c.type == "prompts"},
            dict.fromkeys(CORE_PROMPTS, "core")
            | dict.fromkeys(EXTENDED_PROMPTS, "extended"),
        )
        prompts = list(CATALOG.joinpath("prompts").iterdir())
        self.assertEqual(
            {p.name for p in prompts}, {f"{p}.prompt.md" for p in expected}
        )
        for prompt in prompts:
            self.assertTrue(prompt.read_text(encoding="utf-8").strip())

    def test_core_profile_contains_only_original_agents_and_skills(self) -> None:
        selected = Catalog().select({}, "core")
        self.assertEqual(
            {(c.type, c.id) for c in selected},
            {("agents", name) for name in CORE_AGENTS}
            | {("skills", name) for name in CORE_SKILLS},
        )
        self.assertEqual(len(selected), 12)

    def test_finished_content_has_no_scaffold_tokens(self) -> None:
        for resource in (
            resource
            for kind in TYPES
            for resource in descendants(CATALOG.joinpath(kind))
        ):
            if resource.name.endswith(".tmpl"):
                continue
            with self.subTest(resource=str(resource)):
                text = resource.read_text(encoding="utf-8")
                self.assertNotRegex(text, r"\{\{[^}]+\}\}|\[TODO\]")


if __name__ == "__main__":
    unittest.main()
