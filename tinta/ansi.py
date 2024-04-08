#!/usr/bin/env python

# Tinta
# Copyright 2024 github.com/brandoncript

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# If you use this software, you must also agree under the terms of the Hippocratic License 3.0 to not use this software in a way that directly or indirectly causes harm. You can find the full text of the license at https://firstdonoharm.dev.

"""This class is a low-level helper class for managing colors in Tinta."""

import configparser
import sys
from pathlib import Path
from typing import List, Optional, Type, Union

from .stylize import ansi_color_to_int, is_ansi_str
from .typ import MissingColorError
from .utils import measure

colors_ini = configparser.ConfigParser()


@measure
def _alias_keys(colors: "Union[AnsiColors, Type[AnsiColors]]", search: str, repl: str):
    """Sets up an alias key for a color."""

    for k in (k for k in colors_ini["colors"].keys() if search.lower() in k.lower()):
        alias_key = k.replace(search.lower(), repl.lower())
        if alias_key not in colors_ini["colors"] and alias_key not in colors.__dict__:
            if isinstance(colors, AnsiColors):
                colors.__setattr__(alias_key, int(colors_ini["colors"][k]))
            else:
                setattr(colors, alias_key, int(colors_ini["colors"][k]))
            colors_ini["colors"][alias_key] = colors_ini["colors"][k]


@measure
def _check_path(path: Optional[Union[str, Path]] = None):
    """Loads colors from a file."""
    path = Path(path) if path else Path(__file__).parent / "colors.ini"
    if not path.is_absolute():
        path = Path().cwd() / path
    if not path.exists():
        raise FileNotFoundError(
            f"Tinta failed to load colors, '{path}' does not exist."
        )

    # if path is a dir, look for colors.ini
    if path.is_dir():
        path = path / "colors.ini"

    # if there is still no colors.ini file, look for one in Path.cwd() or PYTHONPATH
    if not path.exists():
        for p in [Path().cwd(), Path(sys.path[0])]:
            if (p / "colors.ini").exists():
                path = p / "colors.ini"
                break

    if not path.exists():
        raise FileNotFoundError(
            f"Tinta failed to load colors, could not find 'colors.ini' in cwd or in PYTHONPATH. Please provide a valid path to a colors.ini file."
        )
    return path


class AnsiColors:
    """Color builder for Tinta's console output.

    ANSI color map for console output. Get a list of colors here =
    http://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html#256-colors

    Or run Tinta.discover() to see all 256 colors on your system.

    You can change the colors the terminal outputs by changing the
    ANSI values in colors.ini.
    """

    _initialized = False
    _colors_ini_path = None

    @measure
    def __init__(self, path: Optional[Union[str, Path]] = None):

        if not AnsiColors._initialized:
            path = _check_path(path)
            AnsiColors.load_colors(path)
            AnsiColors._colors_ini_path = path
            AnsiColors._initialized = True

    @classmethod
    @measure
    def load_colors(cls, path: Union[str, Path]):
        """Loads colors from a file."""

        colors_ini.read(path)
        for k, v in colors_ini["colors"].items():
            setattr(cls, k, int(v))

        _alias_keys(cls, "gray", "grey")
        _alias_keys(cls, "grey", "gray")

    @measure
    def get(self, color: str) -> int:
        """Returns the ANSI code for a color.

        Args:
            color (str): A color name.

        Returns:
            int: The ANSI code for the color.
        """

        if color == "default":
            return 0

        if is_ansi_str(color):
            return ansi_color_to_int(color)

        if color not in colors_ini["colors"]:
            raise MissingColorError(f"Color '{color}' not found in colors.ini.")

        return int(getattr(self, color))

    @measure
    def reverse_get(self, code: int, ignore_errors: bool = False) -> str:
        """Returns the color name for an ANSI code.

        Args:
            code (int): An ANSI code.
            ignore_errors (bool, optional): If True, will return None if the code is not found. Defaults to False.

        Returns:
            str: The color name for the code.
        """

        if code == 0:
            return "default"

        for k, v in colors_ini["colors"].items():
            if int(v) == code:
                return k

        if not ignore_errors:
            raise MissingColorError(
                f"Color with ANSI code '{code}' not found in colors.ini."
            )

        return "[undefined color]"

    @measure
    def list_colors(self) -> List[str]:
        """Returns a list of all colors in the colors.ini file."""
        return list(colors_ini["colors"].keys())
