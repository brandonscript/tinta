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
from typing import List, Optional, Union

from .typ import MissingColorError

config = configparser.ConfigParser()


class AnsiColors:
    """Color builder for Tinta's console output.

    ANSI color map for console output. Get a list of colors here =
    http://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html#256-colors

    Or run Tinta.discover() to see all 256 colors on your system.

    You can change the colors the terminal outputs by changing the
    ANSI values in colors.ini.
    """

    def __init__(self, path: Optional[Union[str, Path]] = None):
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

        config.read(path)
        for k, v in config["colors"].items():
            self.__setattr__(k, int(v))

    def get(self, color: str) -> int:
        """Returns the ANSI code for a color.

        Args:
            color (str): A color name.

        Returns:
            int: The ANSI code for the color.
        """

        if color == "default":
            return 0

        if color not in config["colors"]:
            raise MissingColorError(f"Color '{color}' not found in colors.ini.")

        return int(config["colors"][color])

    def reverse_get(self, code: int) -> str:
        """Returns the color name for an ANSI code.

        Args:
            code (int): An ANSI code.

        Returns:
            str: The color name for the code.
        """
        for k, v in config["colors"].items():
            if int(v) == code:
                return k

        raise MissingColorError(
            f"Color with ANSI code '{code}' not found in colors.ini."
        )

    def list_colors(self) -> List[str]:
        """Returns a list of all colors in the colors.ini file."""
        return list(config["colors"].keys())
