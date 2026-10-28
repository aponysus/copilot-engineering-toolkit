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

## JetBrains

Open the same copied fixture root. Record IDE name/version, Copilot plugin
version, and selected harness. Inspect the IDE's Copilot Customizations controls,
confirm the repository instruction file and agent selection, then repeat the
file-reading and skill-loading checks above. Test a copied prompt file when
supported; record copy/paste fallback separately from native prompt discovery.

For .NET onboarding, open the intended solution explicitly and record which
solution and SDK the IDE uses. Directory visibility does not prove semantic
loading or a successful build. See [native locations](native-locations.md) for
host-specific limitations. No JetBrains live results are published yet.
