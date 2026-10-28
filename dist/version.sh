#!/usr/bin/env bash
# Tinta — Copyright (c) 2026 github.com/brandonscript
# Licensed under the MIT License. See LICENSE.
#
# Bump (or inspect) the package version across all surfaces that declare it.
#
# Usage:
#   ./dist/version.sh 1.1.0          # set version everywhere
#   ./dist/version.sh --show         # print current versions
#   ./dist/version.sh --check        # exit 1 if surfaces disagree
#   ./dist/version.sh --dry-run 1.1.0

set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"

PYPROJECT="$ROOT/pyproject.toml"
SETUP_PY="$ROOT/setup.py"
INIT_PY="$ROOT/tinta/__init__.py"
README="$ROOT/README.md"

DRY_RUN=false
MODE="set"
NEW_VERSION=""

usage() {
    cat <<'EOF'
Usage:
  ./dist/version.sh <version>       Set package version across all surfaces
  ./dist/version.sh --show          Show versions currently declared
  ./dist/version.sh --check         Verify all surfaces match (exit 1 if not)
  ./dist/version.sh --dry-run <ver> Show what would change without writing

Surfaces updated:
  - pyproject.toml  [project].version
  - pyproject.toml  [tool.poetry].version
  - setup.py        version="..."
  - tinta/__init__.py  __version__
  - README.md       shields.io version badge

Not updated (intentionally):
  - poetry.lock / dependency versions
  - python_version / target-version / minversion tool settings
  - MANIFEST.in, poetry.toml, requirements.txt (no package version)
  - GitHub Actions (reads version from pyproject.toml at release time)
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        --show|-s)
            MODE="show"
            shift
            ;;
        --check|-c)
            MODE="check"
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -*)
            echo "error: unknown option: $1" >&2
            usage >&2
            exit 1
            ;;
        *)
            NEW_VERSION="$1"
            shift
            ;;
    esac
done

if [[ "$MODE" == "set" && -z "$NEW_VERSION" && "$DRY_RUN" == false ]]; then
    # default to show when no args
    MODE="show"
fi

if [[ "$DRY_RUN" == true && -z "$NEW_VERSION" ]]; then
    echo "error: --dry-run requires a version argument" >&2
    exit 1
fi

if [[ -n "$NEW_VERSION" ]]; then
    if ! [[ "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+([a-zA-Z0-9.+-]*)?$ ]]; then
        echo "error: invalid version '$NEW_VERSION' (expected e.g. 1.2.3 or 1.2.3a1)" >&2
        exit 1
    fi
    MODE="set"
fi

# --- helpers ---------------------------------------------------------------

read_project_version() {
    python3 - <<'PY'
from pathlib import Path
try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
print(data["project"]["version"])
PY
}

read_poetry_version() {
    python3 - <<'PY'
from pathlib import Path
try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
print(data.get("tool", {}).get("poetry", {}).get("version", ""))
PY
}

read_setup_version() {
    python3 - <<'PY'
import re
from pathlib import Path
text = Path("setup.py").read_text(encoding="utf-8")
m = re.search(r'version\s*=\s*["\']([^"\']+)["\']', text)
print(m.group(1) if m else "")
PY
}

read_init_version() {
    python3 - <<'PY'
import re
from pathlib import Path
text = Path("tinta/__init__.py").read_text(encoding="utf-8")
m = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
print(m.group(1) if m else "")
PY
}

read_readme_version() {
    python3 - <<'PY'
import re
from pathlib import Path
text = Path("README.md").read_text(encoding="utf-8")
m = re.search(r"badge/version-([^-\s]+)-green\.svg", text)
print(m.group(1) if m else "")
PY
}

show_versions() {
    local project poetry setup init readme
    project=$(read_project_version)
    poetry=$(read_poetry_version)
    setup=$(read_setup_version)
    init=$(read_init_version)
    readme=$(read_readme_version)

    echo "Package version surfaces:"
    printf "  %-28s %s\n" "pyproject.toml [project]" "$project"
    printf "  %-28s %s\n" "pyproject.toml [tool.poetry]" "$poetry"
    printf "  %-28s %s\n" "setup.py" "$setup"
    printf "  %-28s %s\n" "tinta/__init__.py" "$init"
    printf "  %-28s %s\n" "README.md badge" "$readme"
}

check_versions() {
    local project poetry setup init readme
    project=$(read_project_version)
    poetry=$(read_poetry_version)
    setup=$(read_setup_version)
    init=$(read_init_version)
    readme=$(read_readme_version)

    show_versions
    echo

    local ok=true
    for pair in \
        "pyproject [tool.poetry]:$poetry" \
        "setup.py:$setup" \
        "tinta/__init__.py:$init" \
        "README.md badge:$readme"
    do
        local label="${pair%%:*}"
        local value="${pair#*:}"
        if [[ "$value" != "$project" ]]; then
            echo "mismatch: $label is '$value' (expected '$project')" >&2
            ok=false
        fi
    done

    if [[ "$ok" == true ]]; then
        echo "OK — all surfaces are $project"
        return 0
    fi
    echo "FAIL — version surfaces are out of sync" >&2
    return 1
}

set_versions() {
    local version="$1"
    local dry="$2"

    python3 - "$version" "$dry" <<'PY'
import re
import sys
from pathlib import Path

version = sys.argv[1]
dry_run = sys.argv[2] == "true"
root = Path(".")

changes: list[tuple[str, str, str]] = []


def replace_file(path: Path, pattern: str, repl: str, flags: int = 0) -> None:
    text = path.read_text(encoding="utf-8")
    new_text, n = re.subn(pattern, repl, text, flags=flags)
    if n == 0:
        raise SystemExit(f"error: no match in {path} for pattern: {pattern!r}")
    old_snip = re.search(pattern, text, flags=flags)
    old_val = old_snip.group(0) if old_snip else "?"
    suffix = f" ({n} occurrences)" if n > 1 else ""
    changes.append((str(path) + suffix, old_val, repl))
    if not dry_run:
        path.write_text(new_text, encoding="utf-8")


# pyproject.toml: only [project] and [tool.poetry] package versions
pyproject = root / "pyproject.toml"
text = pyproject.read_text(encoding="utf-8")
sections = ("[project]", "[tool.poetry]")
new_lines: list[str] = []
current: str | None = None
n = 0
old_val = None
for line in text.splitlines(keepends=True):
    stripped = line.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        current = stripped
    if (
        current in sections
        and re.match(r'^version\s*=\s*"[^"]+"\s*$', stripped)
    ):
        if old_val is None:
            old_val = stripped
        n += 1
        nl = "\n" if line.endswith("\n") else ""
        indent = line[: len(line) - len(line.lstrip(" \t"))]
        line = f'{indent}version = "{version}"{nl}'
    new_lines.append(line)
if n == 0:
    raise SystemExit("error: no package version fields found in pyproject.toml")
suffix = f" ({n} occurrences)" if n > 1 else ""
changes.append((f"pyproject.toml{suffix}", old_val or "?", f'version = "{version}"'))
if not dry_run:
    pyproject.write_text("".join(new_lines), encoding="utf-8")

# setup.py
replace_file(
    root / "setup.py",
    r'version\s*=\s*["\'][^"\']+["\']',
    f'version="{version}"',
)

# tinta/__init__.py
replace_file(
    root / "tinta" / "__init__.py",
    r'__version__\s*=\s*["\'][^"\']+["\']',
    f'__version__ = "{version}"',
)

# README badge
replace_file(
    root / "README.md",
    r"badge/version-[^-\s]+-green\.svg",
    f"badge/version-{version}-green.svg",
)

prefix = "Would update" if dry_run else "Updated"
print(f"{prefix} package version → {version}")
for path, old, new in changes:
    print(f"  {path}")
    print(f"    {old}  →  {new}")
PY
}

# --- main ------------------------------------------------------------------

case "$MODE" in
    show)
        show_versions
        ;;
    check)
        check_versions
        ;;
    set)
        set_versions "$NEW_VERSION" "$DRY_RUN"
        echo
        if [[ "$DRY_RUN" == true ]]; then
            echo "(dry run — no files written)"
        else
            check_versions
        fi
        ;;
esac
