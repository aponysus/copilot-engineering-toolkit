"""Validate the distributable native content, including installed resources."""

from importlib.resources import files
import unittest

import yaml


CATALOG = files("copilot_engineering_toolkit").joinpath("catalog")
CORE_SKILLS = {
    "repository-onboarding", "work-item-analysis", "change-impact-analysis",
    "test-design", "legacy-contract-analysis", "api-contract-evolution",
    "database-change-safety", "incident-triage",
}
CORE_AGENTS = {"architect", "systems-investigator", "test-engineer", "documentation"}


def frontmatter(resource):
    text = resource.read_text(encoding="utf-8")
    opening, metadata, body = text.split("---", 2)
    if opening or not body.strip():
        raise ValueError(f"Missing frontmatter or body: {resource.name}")
    data = yaml.safe_load(metadata)
    if not isinstance(data, dict):
        raise ValueError(f"Frontmatter must be a mapping: {resource.name}")
    return data, body


def descendants(resource):
    for child in resource.iterdir():
        if child.is_dir():
            yield from descendants(child)
        else:
            yield child


class ContentTests(unittest.TestCase):
    def test_all_eight_core_skills_have_valid_native_metadata(self):
        skills = list(CATALOG.joinpath("skills").iterdir())
        self.assertEqual({item.name for item in skills}, CORE_SKILLS)
        for folder in skills:
            with self.subTest(skill=folder.name):
                data, _ = frontmatter(folder.joinpath("SKILL.md"))
                self.assertEqual(data["name"], folder.name)
                self.assertRegex(data["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
                self.assertLessEqual(len(data["name"]), 64)
                self.assertIsInstance(data["description"], str)
                self.assertTrue(data["description"].strip())
                self.assertLessEqual(len(data["description"]), 1024)

    def test_core_agents_preserve_repository_context_without_model_or_tool_pins(self):
        agents = list(CATALOG.joinpath("agents").iterdir())
        self.assertEqual({a.name for a in agents}, {f"{a}.agent.md" for a in CORE_AGENTS})
        for agent in agents:
            with self.subTest(agent=agent.name):
                data, _ = frontmatter(agent)
                self.assertEqual(agent.name, f'{data["name"]}.agent.md')
                self.assertIsInstance(data["description"], str)
                self.assertTrue(data["description"].strip())
                self.assertIs(data["include-custom-instructions"], True)
                self.assertNotIn("model", data)
                self.assertNotIn("tools", data)

    def test_language_rules_have_intended_scope(self):
        # Each shipped glob intentionally covers one language at root and below.
        for language, extension in {"csharp": "cs", "sql": "sql", "python": "py", "go": "go"}.items():
            with self.subTest(language=language):
                data, _ = frontmatter(CATALOG.joinpath("instructions", f"{language}.instructions.md"))
                self.assertEqual(data["applyTo"], f"**/*.{extension}")

    def test_templates_are_explicitly_incomplete(self):
        templates = list(CATALOG.joinpath("templates").iterdir())
        self.assertEqual({t.name for t in templates}, {"base", "dotnet", "python", "go"})
        for folder in templates:
            with self.subTest(template=folder.name):
                text = folder.joinpath("AGENTS.md.tmpl").read_text(encoding="utf-8")
                self.assertIn("{{PROJECT_NAME}}", text)
                self.assertIn("{{TEST_COMMAND}}", text)
                self.assertEqual(text.count("{{"), text.count("}}"))

    def test_task_prompts_are_packaged(self):
        expected = {"analyze-work-item", "bootstrap-agents", "investigate-behavior", "review-change"}
        prompts = list(CATALOG.joinpath("prompts").iterdir())
        self.assertEqual({p.name for p in prompts}, {f"{p}.prompt.md" for p in expected})
        for prompt in prompts:
            self.assertTrue(prompt.read_text(encoding="utf-8").strip())

    def test_finished_content_has_no_scaffold_tokens(self):
        for resource in descendants(CATALOG):
            if resource.name.endswith(".tmpl"):
                continue
            with self.subTest(resource=str(resource)):
                text = resource.read_text(encoding="utf-8")
                self.assertNotRegex(text, r"\{\{[^}]+\}\}|\[TODO\]")


if __name__ == "__main__":
    unittest.main()
