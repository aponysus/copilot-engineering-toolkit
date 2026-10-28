# Installer usage and safety

For a first installation, use the [manual quick start](../README.md#quick-start-copy-one-agent-and-skill).
The optional `copilot-toolkit` CLI helps repeat users install selected content
across projects. It reads one packaged catalog and performs local operations only.
It does not authenticate, download content, execute Copilot, or change remotes.
Python 3.11+ is required; there are no runtime dependencies. From an uninstalled
clone, change to `src/` and use `python -B -m copilot_engineering_toolkit` in place
of `copilot-toolkit`. The `-B` option avoids Python bytecode cache writes.

## Select content

```sh
copilot-toolkit catalog
copilot-toolkit catalog --type skills
copilot-toolkit paths --surface cli
copilot-toolkit install user --surface cli --profile starter --dry-run
copilot-toolkit install project /work/example --skills work-item-analysis,test-design --agents systems-investigator --dry-run
copilot-toolkit install project /work/example --prompts analyze-work-item --instructions python,project-context --dry-run
```

Replace `/work/example` with an existing directory, or a quoted Windows path
such as `"C:\work\example"`. Paths must be direct and must not contain `..`.
With no selection flags, the starter profile installs only Systems Investigator,
`work-item-analysis`, and `change-impact-analysis`. Select `--profile core`
explicitly for all four agents and eight skills. Explicit component flags select
only those components unless you also pass a profile; then they add to that
profile, without duplicates. Comma-separated IDs must be nonempty and valid;
`catalog` lists IDs qualified by type, tier, and permitted destinations.

Earlier versions defaulted to core. Existing installations are left intact;
switching profiles does not remove previously installed components.

Prompts and path instructions are project-only. `--instructions project-context`
creates the small `.github/copilot-instructions.md` bridge. Templates are used
only by `init`. No component installation initializes or synchronizes `AGENTS.md`.
Skills include their supporting files, preserving relative locations.

## User preferences and locations

```sh
copilot-toolkit install user --surface cli --global engineering --dry-run
copilot-toolkit install user --surface cli --global engineering,preferences-optional --dry-run
copilot-toolkit install user --surface cli --home /work/test-copilot --profile starter --dry-run
copilot-toolkit install user --surface jetbrains --global engineering --global-path /work/ide/global-copilot-instructions.md --dry-run
```

Global content is selected explicitly and composed into one file in catalog
order. Selecting just the personal overlay does not automatically include the
baseline. The installer does not merge with an existing file; inspect the diff
or manually integrate the text if you want to preserve customizations.

For CLI, `--home` means the **configuration directory**, not the user's operating
system home. Its precedence is explicit `--home`, then `COPILOT_HOME`, then
`~/.copilot`. `--global-path` overrides only the global instructions file.
`paths` prints exact destinations without creating them.

For JetBrains, only global content is supported at user scope. Install agents
and skills at project scope. macOS and Windows defaults follow the documented
locations in [native locations](native-locations.md); Linux requires
`--global-path` taken from the IDE's Customizations settings. Unknown locations
are never silently invented.

## Bootstrap a project

```sh
copilot-toolkit init /work/example --template base --dry-run
copilot-toolkit init /work/example --template base
copilot-toolkit audit project /work/example
```

Choose `dotnet`, `python`, or `go` for the corresponding context. For a
multi-solution .NET repository, initialize once at the repository root and use
the bootstrap prompt to establish solution selection, framework/platform
constraints, and real test commands. No command here inspects source to fill
placeholders. Existing project instructions remain authoritative; preview any
intentional replacement and keep useful local content.

## Writes, conflicts, and recovery

To update copied toolkit content, obtain a reviewed newer checkout or wheel and
repeat the same selections with `--dry-run`. Compare changes before applying
them. Keep custom project facts in project-owned instructions; there is no
automatic update or merge process.

Every operation preflights all sources and destinations. Dry-run prints unified
diffs and creates no directories, files, or backups. Identical bytes are a no-op,
including file modification time. Installation also prints its diffs before
writing. If any existing file differs, the operation refuses all writes unless
`--force` is explicit. `--dry-run --force` previews the replacement only.

Forced replacements first write a timestamped sibling backup containing the exact
old bytes and preserving file permissions where the platform supports them. A
new file starts with private permissions. Completed files and backup paths are
reported. Restore a chosen original manually from its reported backup after
inspecting the current file; backups are never automatically deleted.

Writes use a same-directory temporary file. New files are published with a
no-overwrite hard link; replacements use atomic rename after backup. Filesystems
without the required operation fail safely rather than falling back to an unsafe
overwrite. Atomicity and permission behavior depend on the filesystem/platform.
Windows ACLs and extended metadata are not copied as a portable POSIX mode.

Symlinks and Windows reparse points are refused in destinations and ancestors,
including dangling links. Use the actual directory path if an OS-owned alias
(for example macOS `/var`) intervenes. Parent traversal is rejected. Files and
existing parent identities are rechecked before writing, including after backup.
These checks detect ordinary concurrent edits; they are not a security boundary
against hostile concurrent filesystem manipulation. Avoid concurrent writers.

Multi-file installation is not transactional. An I/O failure can leave completed
files, directories, and backups. The error reports how many files were updated;
inspect the reported paths before retrying or restoring. Unrelated files are
never deleted, and no hidden synchronization runs later.

## Read-only diagnostics and exit codes

```sh
copilot-toolkit audit project /work/example
copilot-toolkit audit user --surface cli
copilot-toolkit audit user --surface jetbrains --global-path /work/ide/global-copilot-instructions.md
```

Audit reports known guidance files, empty content, placeholders, missing metadata,
skill-name mismatches, and exact duplicate text. Metadata checks are heuristics,
not full YAML validation. It does not establish semantic consistency, correct
glob application, or client loading. Inspect those separately. It never executes
commands found in documents or runs project tests.

Project audits stay inside the requested root, skip links and common generated
directories, and limit content reads to recognized files of at most 1 MiB. User
audits inspect only the selected global file and CLI agent/skill directories;
credentials and arbitrary home directories are not scanned. File contents are
not printed by audit. Preview diffs, in contrast, deliberately show selected
destination content.

- `0`: success, identical install, clean preview, or audit with advisory warnings.
- `1`: conflict (including a dry-run conflict), invalid selection/catalog/path,
  unsupported location, or filesystem failure.
- `2`: command-line syntax error.

Filesystem behavior has been tested on Linux. Windows/macOS path resolution has
unit coverage; native filesystem and Copilot/JetBrains checks remain unverified.
