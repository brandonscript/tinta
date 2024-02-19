#!/usr/bin/env python

# Tinta
# Copyright 2024 github.com/brandoncript

# This program is bound to the Hippocratic License 2.1
# Full text is available here:
# https://firstdonoharm.dev/version/2/1/license

# Further to adherence to the Hippocratic License, permission is hereby
# granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software") under the terms of the
# MIT License to deal in the Software without restriction, including without
# limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and / or sell copies of the Software, and to permit persons
# to whom the Software is furnished to do so, subject to the conditions layed
# out in the MIT License.

# Where a conflict or dispute would arise between these two licenses, HLv2.1
# shall take precedence.

"""Tinta is a magical console output tool with support for printing in beautiful
colors and with rich formatting, like bold and underline. It's so pretty,
it's almost like a unicorn.
"""

import configparser
import os
import re
import sys
from pathlib import Path
from typing import Any, cast, Optional

from typing_extensions import deprecated, Self

from .ansi import AnsiColors
from .colorize import colorize
from .discover import discover as _discover
from .typ import copy_kwargs, MissingColorError

config = configparser.ConfigParser()

CURSOR_UP_ONE = "\x1b[1A"
ERASE_LINE = "\x1b[2K"
SEP = os.getenv("TINTA_SEPARATOR", " ")
STEALTH = os.environ.get("TINTA_STEALTH")
PREFER_PLAINTEXT = os.environ.get("TINTA_PLAINTEXT")


class _MetaTinta(type):

    def __init__(cls, name, bases, dct):
        super(_MetaTinta, cls).__init__(name, bases, dct)
        cls.colors = AnsiColors()

    def load_colors(cls, path: str | Path):
        loaded_colors = AnsiColors(path)

        # Check if any of the color names loaded match the built-in methods. If so, raise an error.
        for col in loaded_colors.list_colors():
            if hasattr(cls, col):
                raise AttributeError(
                    f"Cannot overwrite built-in method '\
                        {col}' with color name. Please rename the color in '{path}'."
                )

        # Add the loaded colors to the Tinta class
        cls.colors = loaded_colors


class Tinta(metaclass=_MetaTinta):
    """Tinta is a magical console output tool with support for printing in
    beautiful colors and with rich formatting, like bold and underline. It's
    so pretty, it's almost like a unicorn.

    All public methods chain together to form a builder pattern, e.g.:

    (Tinta('Some plain text')
        .white(' white')
        .blue(' blue')
        .red(' red')
        .bold().red(' bold red')
        .dark_gray()
        .dim(' dim').print())

    Args:
        *s (tuple(Any)): A sequence of one or more text strings, to be joined together.
        sep (str): Used to join segment strings. Defaults to ' '.

    Attributes:
        color (str, int):           A color string or ansi color code (int),
                                    e.g. 'white' or 42
        style (str):                A style string, e.g. 'bold', 'dim', 'underline'.
                                    Multiple styles are joined with a +
        parts (list):               A list of Part objects.
        get_parts(style: str):      Returns a list of string parts, or a list of Parts.

    Methods:
        to_str() -> str:           Returns a compiled rich text string, or use plaintext=True for plaintext.
        push() -> self:             Adds segments to this Tinta instance.
        pop(qty: int) -> self:              Removes the last 'qty' segments from this Tinta instance.
        text()                      [deprecated]
        plaintext()                 [deprecated]
        add()                       [deprecated, use push or __call__]
        code()                      [deprecated]
        bold() -> self:             Sets segments to bold.
        underline() -> self:        Sets segments to underline.
        dim() -> self:              Sets segments to a darker, dimmed color.
        normal() -> self:           Removes all styles.
        reset() -> self:            Removes all styles and colors.
        line() -> self:             Adds segments on a new line.
        print():                    Prints the output of a Tinta instance, then resets.
    """

    color: int | str
    colors: AnsiColors

    def __init__(self, *s: Any, color: Optional[str | int] = None, sep: str = SEP):
        """Main intializer for Tinta

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.
        """

        self.color = color or 0  # 0 is the default color for terminals
        self.style: list[str] = []
        self._parts: list["Tinta.Part"] = []
        self._prefixes: list[str] = []

        # Inject ANSI helper functions
        for c in vars(self.colors):
            self._colorizer(c)

        if s:
            self.push(*s, sep=sep)

    def __call__(self, *s: Any, sep: str = SEP) -> "Tinta":
        return self.push(*s, sep=sep)

    def __repr__(self) -> str:
        """Generates a string representation of the current
        Tinta instance.

        Returns:
            str: Plaintext string
        """
        return str(self.to_str(plaintext=True))

    def _colorizer(self, c: str):
        """Generates statically typed color methods
        based on colors.ini.

        Args:
            c (str): Method name of color, e.g. 'pink', 'blue'.
        """
        self.__setattr__(c, self.push)

    @deprecated("Use to_str() instead.")
    def get_text(self, sep: str = SEP) -> str:
        """
        Deprecated. Use to_str() instead.

        Args:
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            str: A rich text string.
        """
        return self.to_str(sep=sep)

    def to_str(self, sep: Optional[str] = None, plaintext: bool = False) -> str:
        """Returns a compiled rich text string, joined by 'sep'. Note that any separators included with a
        part will be returned as part of the string - adding a separator here may result in a double separator.

        # TODO: Add magic punctuation handling for sep, to prevent accidental spaces before punctuation.

        Args:
            sep (str, optional): Used to join strings. Defaults to the separator used when the part was added, or ' '. Setting this will override the part's separator.

        Returns:
            str: A rich text string.
        """

        if not self._parts:
            return ""

        attr = "fmt" if not plaintext else "pln"

        def _get_sep(part: "Tinta.Part") -> str:
            return sep if sep is not None else part.sep

        separated_parts = [Tinta.Part(p.fmt, p.pln, _get_sep(p)) for p in self._parts]
        if separated_parts:
            separated_parts[-1].sep = ""

        return "".join([f"{getattr(p, attr)}{_get_sep(p)}" for p in separated_parts])

    @property
    def parts(self) -> list["Tinta.Part"]:
        """A list of Tinta.Part objects.

        Returns:
            list[Part]: A list of Tinta.Part objects"""

        return self._parts

    @property
    @deprecated("Use parts_fmt instead.")
    def parts_formatted(self) -> list:
        """Returns a list of richly formated string parts

        Returns:
            str: A list of formatted strings."""
        return [part.fmt for part in self._parts]

    @property
    def parts_fmt(self) -> list:
        """Returns a list of richly formated string parts

        Returns:
            str: A list of formatted strings."""
        return [part.fmt for part in self._parts]

    @property
    @deprecated("Use parts_pln instead.")
    def parts_plaintext(self) -> list:
        """Returns a list of plaintext string parts

        Returns:
            str: A list of plaintext strings."""
        return [part.pln for part in self._parts]

    @property
    def parts_pln(self) -> list:
        """Returns a list of plaintext string parts

        Returns:
            str: A list of plaintext strings."""
        return [part.pln for part in self._parts]

    @property
    def parts_esc(self) -> list:
        """Returns a list of escaped formatted string parts, so that special characters are visible (i.e., backslashes are doubled).

        Returns:
            str: A list of esc strings."""
        return [part.esc for part in self._parts]

    @deprecated("Use to_str(plaintext=True) instead.")
    def get_plaintext(self, sep: Optional[str] = None) -> str:
        """Deprecated. Use to_str(plaintext=True) instead.

        Args:
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            str: A plaintext string.
        """
        return self.to_str(sep=sep, plaintext=True)

    def push(self, *s: Any, sep: Optional[str] = SEP) -> "Tinta":
        """Adds segments to this Tinta instance

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """

        # If an empty set of segments is passed, skip to the
        # next segment (to prevent duplicating whitespace).
        if not s:
            return self

        if sep is None:
            sep = SEP

        # Join all s parts with the specified separator
        pln = sep.join([str(x) for x in s])

        # Collect any prefixes that may have been set
        if self._prefixes:
            pln = "".join(self._prefixes) + pln
            self._prefixes = []

        # Generate style string
        style = "+".join(list(set(self.style))) if self.style else None

        fg: int = 0
        if isinstance(self.color, int):
            fg = self.color
        elif isinstance(self.color, str):
            fg = self.colors.get(self.color or "default")

        # TODO: Add support for background colors

        # Generate formatted string
        fmt = colorize(pln, fg=fg, style=style)

        # Append to parts list
        self._parts.append(Tinta.Part(fmt, pln, sep))

        return self

    @deprecated(
        "Use use push() or __call__() directly (e.g. Tinta('text')('more text')) instead."
    )
    def add(self, *s: Any, sep: str = SEP) -> "Tinta":
        """Deprecated. Use push() or just __call__() (e.g. Tinta('text')('more text')) instead.

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        return self.push(*s, sep=sep)

    def pop(self, qty: int = 1) -> "Tinta":
        """Removes the last 'qty' segments from this Tinta instance

        Args:
            qty (int, optional): Number of segments to remove. Defaults to 1.

        Returns:
            self
        """
        for _ in range(min(qty, len(self._parts))):
            self._parts.pop()
        return self

    @deprecated("Use pop() instead.")
    def remove(self, qty: int = 1) -> "Tinta":
        return self.pop(qty)

    # pylint: disable=redefined-outer-name
    def tint(
        self, color: Optional[str | int] = None, *s: Any, sep: str = SEP
    ) -> "Tinta":
        """Adds segments of text colored with the specified color.
        Can be used in place of calling named color methods.

        Args:
            color (str | int, optional): A color name or ANSI color index. Defaults to first argument.
            *s: Any: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """

        if not color:
            if not len(s) > 1:
                raise AttributeError(
                    "If no color is specified, tint() requires at least two arguments."
                )

            color = s[0]
            s = s[1:]

        # if color is numeric integer string, assume it's an ANSI color code
        if isinstance(color, str) and color.isdigit():
            color = int(color)

        # Check if color_name is a valid color if color is a string
        if isinstance(color, str):
            if not hasattr(self.colors, color):  # type: ignore
                raise MissingColorError(
                    f"Invalid color name: {color}. Is it in colors.ini?"
                )
            color = self.colors.get(color)  # type: ignore

        self.color = color
        self.push(*s, sep=sep)
        return self

    @deprecated("Use tint() instead, setting color=<int:A valid ANSI color code>.")
    def code(self, code: int = 0, *s: Any, sep: str = SEP) -> "Tinta":
        """Adds segments of text colored with the specified ANSI code.

        Args:
            *s: Segments of text to add.
            code (int, optional): An ANSI code. Defaults to 0.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self.color = int(code)
        self.push(*s, sep=sep)
        return self

    def bold(self, *s: Any, sep: str = SEP) -> "Tinta":
        """Adds bold segments to this Tinta instance

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self.style.append("bold")
        self.push(*s, sep=sep)
        return self

    @copy_kwargs(bold)
    def b(self, *args, **kwargs):
        return self.bold(*args, **kwargs)

    def underline(self, *s: Any, sep: str = SEP) -> "Tinta":
        """Adds underline segments to this Tinta instance

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self.style.append("underline")
        self.push(*s, sep=sep)
        return self

    @copy_kwargs(underline)
    def u(self, *args, **kwargs):
        return self.underline(*args, **kwargs)

    @copy_kwargs(underline)
    def _(self, *args, **kwargs):
        return self.underline(*args, **kwargs)

    def dim(self, *s: Any, sep: str = SEP) -> "Tinta":
        """Adds darker (dimmed) segments to this Tinta instance

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self.style.append("faint")
        self.push(*s, sep=sep)
        return self

    def normal(self, *s: Any, sep: str = SEP) -> "Tinta":
        """Removes all styles, then adds segments to this Tinta instance

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self.style = []
        # self._prefixes.append('\033[24m\033[21m')
        self.push(*s, sep=sep)
        return self

    def clear(self, *s: Any, sep: str = SEP) -> "Tinta":
        """Removes all styles and colors, then adds segments to this
        Tinta instance

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self.color = 0
        self.normal(*s, sep=sep)
        return self

    @deprecated("Use _() or clear() instead.")
    def reset(self, *s: Any, sep: str = SEP) -> "Tinta":
        return self.push(*s, sep=sep)

    def line(self, *s, sep: str = SEP) -> "Tinta":
        """Adds segments to this Tinta instance, preceded by a new line.

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self._prefixes = [os.linesep]
        self.push(*s, sep=sep)
        return self

    def print(
        self,
        sep: Optional[str] = None,
        end="\n",
        file=sys.stdout,
        flush=False,
        plaintext=False,
        force=False,
    ):
        """Prints a Tinta composite to the console. Once printed,
        this Tinta instance is cleared of all configuration, but can
        can continue to be used to print.

        Env: These environment variables, when set, affect Tinta globally.
            TINTA_STEALTH (not None): Hides all console output. Can be
                                      overridden by 'force'.
            TINTA_PLAINTEXT (not None): Prints all output in plaintext.

        Args:
            sep (str, optional): Used to join strings. Defaults to ' ', or whatever was used when the part was added. Setting this will override the part's separator.
            end (str, optional): String terminator. Defaults to '\n'.
            file (optional): File to write to. Defaults to sys.stdout.
            flush (bool, optional): Clears the current console line.
            plaintext (bool, optional): Prints in plaintext. Defaults to False.
            force (bool, option): Forces printing, overriding TINTA_STEALTH.
        """
        # We don't print if the TINTA_STEALTH env is set
        if STEALTH is not None and not force:
            return

        use_plaintext = True if plaintext or PREFER_PLAINTEXT is not None else False
        print(
            self.to_str(sep=sep, plaintext=use_plaintext),
            end=end,
            file=file,
            flush=flush,
        )

        self.clear()
        self._parts = []
        print("\033[0m", end="", file=file, flush=flush)

    def __getattr__(self, name: str) -> Self:
        """Returns a tinted segment of text.

        Args:
            name (str): Name of the color.

        Returns:
            Tinta: A Tinta instance.
        """

        if not name.startswith("_"):
            if hasattr(self.colors, name):
                return cast(Self, self.tint(color=name))

            else:
                try:
                    return self.__getattribute__(name)
                except AttributeError as e:
                    known_colors = f"- {'- '.join(self.colors.list_colors())}"
                    raise AttributeError(
                        f"Attribute '{name}' not found. Did you try and access a color that doesn't exist? Available colors:\n{known_colors}"
                    ) from e

        return self.__getattribute__(name)

    @staticmethod
    def discover(background=False):
        """Prints all 256 colors in a matrix on your system. If background is True,
        it will print background colors with numbers on top."""
        _discover(background)

    @staticmethod
    def clearline():
        """Clears the current printed line."""

        if sys.stdout:
            sys.stdout.write(CURSOR_UP_ONE)
            sys.stdout.write(ERASE_LINE)
            sys.stdout.flush()

    @staticmethod
    def up():
        """Moves up to the previous line."""

        if sys.stdout:
            sys.stdout.write(CURSOR_UP_ONE)
            sys.stdout.flush()

    class Part:
        """A segment part of text, intended to be joined together
        for a print statement.

        Args:
            fmt (str):      A formatted string of text.
            p (str):        A plaintext representation of fmt.
            sep (str):      Used to join segment strings. Defaults to ' '.
        """

        def __init__(self, fmt: str, pln: str, sep: str = SEP):
            self.fmt = fmt
            self.pln = pln
            self.sep = sep

        def __str__(self):
            return self.fmt

        def __repr__(self):
            return self.__str__()

        @property
        def esc(self):
            return esc(self.fmt)


def escape_ansi(line):
    ansi_escape = re.compile(r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]")
    return ansi_escape.sub("", line)


def esc(string: str, replace: bool = False) -> str:
    """Returns the raw representation of a string. If replace is true,
    replace a double backslash with a single backslash."""
    r = repr(string)[1:-1]  # Strip the quotes from representation
    if replace:
        r = r.replace("\\\\", "\\")
    return r
