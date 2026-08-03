#!/usr/bin/env python

# Tinta — Copyright (c) 2026 github.com/brandonscript
# Licensed under the MIT License. See LICENSE.

"""CLI entry point: ``python -m tinta codegen ...``."""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"-h", "--help"}:
        print(
            "usage: python -m tinta <command> ...\n\n"
            "commands:\n"
            "  codegen   Generate typed color methods from a colors.ini file\n"
        )
        return 0 if argv and argv[0] in {"-h", "--help"} else 1

    command, rest = argv[0], argv[1:]
    if command == "codegen":
        from .codegen import main as codegen_main

        return codegen_main(rest)

    print(f"error: unknown command {command!r}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
