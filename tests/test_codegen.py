#!/usr/bin/env python

# Tinta — Copyright (c) 2026 github.com/brandonscript
# Licensed under the MIT License. See LICENSE.

"""Tests for colors.ini codegen and typed color methods."""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

from tinta import Tinta
from tinta.codegen import (
    filter_color_names,
    generate_subclass_source,
    parse_colors_ini,
    RESERVED_COLOR_NAMES,
    write_typings,
)

O = "\x1b[0m"
ROOT = Path(__file__).resolve().parents[1]


def _mypy_available() -> bool:
    return importlib.util.find_spec("mypy") is not None


def _run_mypy(*paths: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "mypy",
            "--strict",
            "--ignore-missing-imports",
            *paths,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_parse_colors_ini_includes_gray_aliases():
    colors = parse_colors_ini(ROOT / "tinta" / "colors.ini")
    assert "gray" in colors
    assert "grey" in colors
    assert colors["gray"] == colors["grey"]
    assert "dark_gray" in colors
    assert "dark_grey" in colors


def test_filter_rejects_reserved_names():
    valid, conflicts = filter_color_names(
        {"viridian": 42, "bold": 1, "default": 0, "sparkle": 195}
    )
    assert valid == ["sparkle", "viridian"]
    assert conflicts == ["bold", "default"]
    assert "bold" in RESERVED_COLOR_NAMES


def test_generate_subclass_source_emits_methods():
    source = generate_subclass_source(
        {"viridian": 42, "cream": 230}, source="test.ini"
    )
    assert "def viridian(self" in source
    assert 'color="viridian"' in source
    assert "def cream(self" in source
    assert "class Tinta(_Tinta):" in source


def test_generate_subclass_source_rejects_reserved():
    with pytest.raises(ValueError, match="clobber"):
        generate_subclass_source({"bold": 1, "viridian": 42})


def test_write_typings_and_runtime(tmp_path):
    ini = tmp_path / "colors.ini"
    ini.write_text(
        """[colors]
viridian = 42
cream = 230
""",
        encoding="utf-8",
    )
    out = tmp_path / "tinta_colors.py"
    write_typings(ini, out)
    assert out.exists()

    Tinta.load_colors(ini)
    try:
        # Dynamic injection still works without the generated module
        assert Tinta().viridian("v").to_str() == f"\x1b[38;5;42mv{O}"

        # Generated subclass methods call through tint
        spec = importlib.util.spec_from_file_location("tinta_colors_test", out)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert mod.Tinta().cream("c").to_str() == f"\x1b[38;5;230mc{O}"
        assert mod.Tinta().viridian("v").to_str() == f"\x1b[38;5;42mv{O}"
    finally:
        Tinta.load_colors(ROOT / "examples" / "colors.ini")


def test_load_colors_typings_out(tmp_path):
    ini = tmp_path / "colors.ini"
    ini.write_text("[colors]\nsparkle = 195\n", encoding="utf-8")
    out = tmp_path / "typed.py"
    orig = Tinta._colors._colors_ini_path
    try:
        Tinta.load_colors(ini, typings_out=out)
        assert out.exists()
        assert "def sparkle(self" in out.read_text(encoding="utf-8")
        assert Tinta().sparkle("s").to_str() == f"\x1b[38;5;195ms{O}"
    finally:
        Tinta.load_colors(orig)


def test_cli_codegen(tmp_path):
    ini = tmp_path / "colors.ini"
    ini.write_text("[colors]\nviridian = 42\n", encoding="utf-8")
    out = tmp_path / "out.py"
    result = subprocess.run(
        [sys.executable, "-m", "tinta", "codegen", str(ini), "-o", str(out)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "def viridian(self" in out.read_text(encoding="utf-8")


@pytest.mark.skipif(not _mypy_available(), reason="mypy is not installed")
def test_mypy_accepts_generated_custom_color(tmp_path):
    ini = tmp_path / "colors.ini"
    ini.write_text("[colors]\nviridian = 42\n", encoding="utf-8")
    typed = tmp_path / "tinta_colors.py"
    write_typings(ini, typed)

    # Make the generated module importable as a top-level name for the fixture
    fixture = tmp_path / "check_viridian.py"
    fixture.write_text(
        f"""\
from pathlib import Path
import sys
sys.path.insert(0, {str(tmp_path)!r})
from tinta_colors import Tinta

reveal = Tinta().viridian("hello")
reveal.print()
""",
        encoding="utf-8",
    )

    result = _run_mypy(str(fixture))
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.skipif(not _mypy_available(), reason="mypy is not installed")
def test_mypy_accepts_default_color_methods(tmp_path):
    fixture = tmp_path / "check_mint.py"
    fixture.write_text(
        """\
from tinta import Tinta

t: Tinta = Tinta().mint("hello").bold("there")
t.print()
""",
        encoding="utf-8",
    )
    result = _run_mypy(str(fixture))
    assert result.returncode == 0, result.stdout + result.stderr
