#!/usr/bin/env python

# Tinta — Copyright (c) 2026 github.com/brandonscript
# Licensed under the MIT License. See LICENSE.

"""This class is a low-level helper class for managing colors in Tinta."""

import configparser
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type, Union

from .stylize import ansi_color_to_int, is_ansi_str
from .typ import MissingColorError

colors_ini = configparser.ConfigParser()


def _alias_keys(colors: "Union[AnsiColors, Type[AnsiColors]]", search: str, repl: str):
    """Sets up an alias key for a color."""

    for k in (k for k in colors_ini["colors"].keys() if search.lower() in k.lower()):
        alias_key = k.replace(search.lower(), repl.lower())
        if (
            alias_key not in colors_ini["colors"]
            and alias_key not in colors._color_dict
        ):
            colors._color_dict[alias_key] = int(colors_ini["colors"][k])
            colors_ini["colors"][alias_key] = colors_ini["colors"][k]


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
            "Tinta failed to load colors, could not find 'colors.ini' in cwd or in PYTHONPATH. \
            Please provide a valid path to a colors.ini file."
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
    _color_dict: Dict[str, int] = {}

    def __init__(self, path: Optional[Union[str, Path]] = None):

        if not AnsiColors._initialized:
            path = _check_path(path)
            assert path, "AnsiColors(path): path cannot be None"
            AnsiColors.load_colors(path)
            AnsiColors._colors_ini_path = path
            AnsiColors._initialized = True

    @classmethod
    def load_colors(cls, path: Union[str, Path]):
        """Loads colors from a file."""

        colors_ini["colors"] = {}
        colors_ini.read(path)
        cls._color_dict = {k: int(v) for (k, v) in colors_ini["colors"].items()}

        _alias_keys(cls, "gray", "grey")
        _alias_keys(cls, "grey", "gray")

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

        if color not in self._color_dict:
            raise MissingColorError(f"Color '{color}' not found in colors.ini.")

        return self._color_dict[color]

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

        for k, v in self._color_dict.items():
            if v == code:
                return k

        if not ignore_errors:
            raise MissingColorError(
                f"Color with ANSI code '{code}' not found in colors.ini."
            )

        return "[undefined color]"

    @property
    def color_list(self) -> List[str]:
        """Returns a list of all colors in the colors.ini file."""
        return list(self.color_dict.keys())

    @property
    def color_dict(self) -> Dict[str, int]:
        """Returns a dictionary of all colors in the colors.ini file."""
        if not self._color_dict:
            self._color_dict = {k: int(v) for (k, v) in colors_ini["colors"].items()}
        return self._color_dict
