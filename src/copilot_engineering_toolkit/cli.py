"""Offline catalog, installation, and static diagnostics."""

import argparse
import sys
from pathlib import Path

from .audit import audit_project, audit_user
from .catalog import TYPES, Catalog
from .errors import ToolkitError
from .install import absolute, apply, prepare, preview
from .locations import user_locations
from .planning import plan


def _user_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--surface", choices=("cli", "jetbrains"), required=True)
    parser.add_argument(
        "--home",
        type=Path,
        help="exact Copilot CLI configuration directory (overrides COPILOT_HOME)",
    )
    parser.add_argument(
        "--global-path", type=Path, help="exact global instructions file"
    )


def _write_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="preview only; conflict previews exit 1 unless --force is also supplied",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace differing files after backup; never merge",
    )


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="copilot-toolkit", description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("catalog", help="list packaged components")
    listing.add_argument("--type", choices=TYPES)
    paths = commands.add_parser("paths", help="show user destinations without writes")
    _user_options(paths)
    init = commands.add_parser(
        "init", help="create an incomplete project-owned AGENTS.md scaffold"
    )
    init.add_argument("root", type=Path)
    init.add_argument("--template", default="base")
    _write_options(init)
    for command in ("install", "audit"):
        parent = commands.add_parser(command)
        scopes = parent.add_subparsers(dest="scope", required=True)
        for scope in ("user", "project"):
            child = scopes.add_parser(scope)
            if scope == "user":
                _user_options(child)
            else:
                child.add_argument("root", type=Path)
            if command == "install":
                _write_options(child)
                child.add_argument(
                    "--profile",
                    choices=("core",),
                    help="four core agents and eight skills only",
                )
                for kind in ("agents", "skills", "prompts", "instructions", "global"):
                    if scope == "project" and kind == "global":
                        continue
                    child.add_argument(
                        "--" + kind, help=f"comma-separated {kind} IDs; see catalog"
                    )
    return root


def _locations(args: argparse.Namespace) -> dict[str, Path]:
    locations = user_locations(
        args.surface, home=args.home, global_path=args.global_path
    )
    return {key: absolute(value) for key, value in locations.items()}


def main(argv: list[str] | None = None) -> int:
    """Run an offline command and report actionable failures.

    Args:
        argv: Arguments excluding the executable; defaults to process arguments.

    Returns:
        Zero on success or advisory audit findings, one on operational failure.
        Argparse exits with status two for invalid command syntax.
    """
    args = parser().parse_args(argv)
    try:
        if args.command == "paths":
            for key, path in _locations(args).items():
                print(f"{key}: {path}")
            return 0
        if args.command == "audit":
            print(
                "Static diagnostics only: no commands executed; metadata checks are heuristic, not full YAML validation. Native loading and behavior remain unverified."
            )
            findings = (
                audit_project(args.root)
                if args.scope == "project"
                else audit_user(_locations(args))
            )
            for finding in findings:
                print(finding)
            print(
                "Warnings are advisory; inspect instruction interactions and host support manually."
            )
            return 0
        catalog = Catalog()
        if args.command == "catalog":
            for item in catalog.components:
                if args.type is None or args.type == item.type:
                    print(
                        f"{item.type}/{item.id}\t{item.tier}\t{', '.join(item.destinations)}\t{item.path}"
                    )
            return 0
        if args.command == "init":
            selected = catalog.select({"templates": [args.template]})
            writes = plan(catalog, selected, "init", root=args.root)
        else:
            selections = {}
            for kind in ("agents", "skills", "prompts", "instructions", "global"):
                value = getattr(args, kind, None)
                if value is not None:
                    selections[kind] = [part.strip() for part in value.split(",")]
            selected = catalog.select(selections, args.profile)
            if args.scope == "project":
                writes = plan(catalog, selected, "project", root=args.root)
            else:
                if args.surface == "jetbrains" and any(
                    item.type != "global" for item in selected
                ):
                    raise ToolkitError(
                        "JetBrains user installation supports only --global engineering,preferences-optional. Install agents and skills in project scope."
                    )
                writes = plan(
                    catalog,
                    selected,
                    "user-" + args.surface,
                    locations=_locations(args),
                )
        prepared = prepare(writes)
        print(preview(prepared), end="")
        if args.dry_run:
            conflict = any(
                not item.unchanged and item.before.content is not None
                for item in prepared
            )
            if conflict and not args.force:
                print(
                    "Conflict: existing content differs. No writes made; use --force only after reviewing the diff.",
                    file=sys.stderr,
                )
                return 1
            return 0
        apply(prepared, force=args.force)
        return 0
    except (ToolkitError, OSError, UnicodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
