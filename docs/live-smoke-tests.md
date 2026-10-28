# Live client smoke tests

Use a copied synthetic fixture outside the toolkit checkout. Do not use company
code or active personal instruction directories for these checks. Record the
client version, operating system, active model, instruction scope, and observed
results. A successful file copy is not evidence of client discovery.

## GitHub Copilot CLI

1. Check `copilot --version` and `copilot --help` to confirm the executable is
   **GitHub Copilot CLI**. AWS Copilot uses the same executable name and is an
   unrelated deployment tool. Do not run its initialization commands for this task.
2. Copy `evals/fixtures/missing_sql/` into an isolated target directory and install
   `systems-investigator`, `legacy-contract-analysis`, and `project-context`:

   ```sh
   copilot-toolkit install project /work/copilot-smoke --agents systems-investigator --skills legacy-contract-analysis --instructions project-context --dry-run
   copilot-toolkit install project /work/copilot-smoke --agents systems-investigator --skills legacy-contract-analysis --instructions project-context
   ```

3. Add a short `AGENTS.md` to this temporary root with a distinctive harmless
   convention, such as “Call this synthetic application Copper Finch.” Start a
   fresh client session at that root. Inspect `/instructions` and the agent
   selector, select Systems Investigator, and ask it to identify the application
   and trace `CashDist`. Verify quoted symbols and paths against the fixture.
4. Ask to use `legacy-contract-analysis`. Capture a loading indicator or tool
   evidence if the client exposes one; availability and actual loading are
   separate observations. The expected reasoning is in the evaluator guide,
   which should remain outside the client's available roots.
5. Repeat a small read-only question with Architect installed. Verify repository
   context both as a selected session agent and as a custom subagent where the
   host supports it. Explicitly request any delegation. Do not assume the
   frontmatter setting alone proves inheritance.
6. Inspect the target diff. An investigation should not alter production files.
   This demonstrates observed behavior, not an enforced read-only sandbox.

GitHub documents [instruction inspection and custom-subagent inheritance](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference).
Use the active version's controls; record unsupported features instead of
inventing equivalent results. Do not change organization policy or authentication
configuration to bypass an unavailable feature.

## Rider and other JetBrains IDEs

This check needs no Python and no real-task comparison. Copy
`evals/fixtures/api_consumers/` to a temporary folder outside the toolkit checkout.
From the catalog, manually copy `systems-investigator.agent.md` to
`.github/agents/` and the entire `work-item-analysis/` and
`change-impact-analysis/` skill folders to `.github/skills/` in that temporary root.
Copy `instructions/project-context.md` as `.github/copilot-instructions.md`.
Create `AGENTS.md` there containing:

```markdown
# Copper Finch

This synthetic application's name is Copper Finch.
```

1. Open that root in Rider. Record the IDE and Copilot plugin versions and the
   selected harness. Use the IDE's Copilot Customizations controls to inspect
   the repository instructions. Start a fresh session.
2. Confirm Systems Investigator appears in the agent selector, then select it.
3. Ask: “What is this application's name according to AGENTS.md? Read service.py
   and identify both consumers of the count field. Cite their source locations.
   Do not edit files.” Verify the name, `dashboard`, and `export_row` against the
   source. This checks repository context and source access independently of
   whether the skill is available.
4. Ask: “Use work-item-analysis and change-impact-analysis to assess renaming
   count to item_count. Do not edit files.” Inspect any client-provided loading
   indicators or tool traces for each skill. Record unavailable evidence as
   unverified, even if the response says it used the skills.
5. Check that the source files were not changed. Record agent discovery, source
   access, repository-instruction loading, and skill loading separately. A
   successful answer does not prove every discovery mechanism worked.

If a feature is unavailable, record the limitation and try pasted Markdown only
as a separately identified fallback. There is no need to alter global settings
or install the Python CLI for this check. Test a copied prompt file separately
when your plugin supports it.

For .NET onboarding, open the intended solution explicitly and record which
solution and SDK the IDE uses. Directory visibility does not prove semantic
loading or a successful build. See [native locations](native-locations.md) for
host-specific limitations. No JetBrains live results are published yet.
