#!/usr/bin/env python

# Tinta
# Copyright 2024 github.com/brandoncript

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# If you use this software, you must also agree under the terms of the Hippocratic License 3.0 to not use this software in a way that directly or indirectly causes harm. You can find the full text of the license at https://firstdonoharm.dev.

"""Tinta is a magical console output tool with support for printing in beautiful
colors and with rich formatting, like bold and underline. It's so pretty,
it's almost like a unicorn.
"""

import configparser
import functools
import os
import re
import sys
from itertools import zip_longest
from pathlib import Path
from typing import Any, cast, List, Optional, overload, Union

from deprecated import deprecated

from .ansi import AnsiColors
from .colorize import colorize, ensure_reset, tint, was_reset
from .constants import (
    CURSOR_UP_ONE,
    ERASE_LINE,
    PREFER_PLAINTEXT,
    SEP,
    SMART_FIX_PUNCTUATION,
    STEALTH,
)
from .discover import discover as _discover
from .typ import copy_kwargs, MissingColorError, StringType

config = configparser.ConfigParser()


class _MetaTinta(type):

    def __init__(cls, name, bases, dct):
        super(_MetaTinta, cls).__init__(name, bases, dct)
        cls.colors = AnsiColors()

    def load_colors(cls, path: Union[str, Path]):
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
        clear() -> self:            Removes all styles and colors.
        line() -> self:             Adds segments on a new line.
        print():                    Prints the output of a Tinta instance, then clears.
    """

    _initialized = False
    _known_colors: dict[str, Any] = {}
    color: Union[int, str]
    colors: AnsiColors

    def __init__(
        self, *s: Any, color: Optional[Union[str, int]] = None, sep: str = SEP
    ):
        """Main intializer for Tinta

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.
        """

        self.color = color or 0  # 0 is the default color for terminals
        self.style: List[str] = []
        self._parts: List["Tinta.Part"] = []
        self._prefixes: List[str] = []

        # Inject ANSI helper functions
        if not Tinta._initialized:
            Tinta._known_colors = vars(self.colors)
            Tinta._initialized = True
        for c in Tinta._known_colors:
            self.__setattr__(c, functools.partial(self.tint, c))

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

    def __str__(self) -> str:
        """Generates a string representation of the current
        Tinta instance, colorized.

        Returns:
            str: Colorized string"""

        return self.to_str()

    def _get_sep(
        self,
        p: "Tinta.Part",
        next_p: Optional["Tinta.Part"],
        sep: Optional[str],
    ) -> str:
        if not next_p:
            return ""
        return sep if sep is not None else p.sep

    def _get_str(
        self,
        attr: StringType,
        p: "Tinta.Part",
        next_p: Optional["Tinta.Part"] = None,
        sep: Optional[str] = None,
        fix_punc: bool = SMART_FIX_PUNCTUATION,
    ) -> str:

        s: str = getattr(p, attr)

        next_char_is_punc = (
            next_p.pln[0]
            in [
                ".",
                ",",
                ";",
                ":",
                "!",
                "?",
            ]
            if fix_punc and next_p and next_p.pln
            else False
        )

        punc_affects_sep = (
            next_char_is_punc
            and any(
                [
                    (len(next_p.pln) == 1),
                    (len(next_p.pln) > 1 and next_p.pln[1] == " "),
                ]
            )
            if next_p and next_p.pln
            else False
        )

        next_char_is_newline = bool(next_p and next_p.pln.startswith(os.linesep))
        last_char_is_newline = p.pln.endswith(os.linesep)
        newline_affects_punc = last_char_is_newline or next_char_is_newline

        should_ignore_sep = punc_affects_sep or newline_affects_punc

        if not should_ignore_sep:
            s = f"{s}{self._get_sep(p, next_p, sep)}"

        # TODO: Not certain we ever want to do this, it has too many false negatives
        # if fix_punc:
        #     s = re.sub(r"(\w)\s+([.,;:!?])", r"\1\2", s)

        if next_p is None and p.has_formatting:
            if attr == "fmt":
                s = ensure_reset(s)
            elif attr == "esc":
                s = esc(ensure_reset(s))

        return s

    def to_str(
        self,
        sep: Optional[str] = None,
        plaintext: bool = False,
        escape_ansi: bool = False,
        fix_punctuation: bool = SMART_FIX_PUNCTUATION,
    ) -> str:
        """Returns a compiled rich text string, joined by 'sep'. Note that any separators included with a
        part will be returned as part of the string - adding a separator here may result in a double separator.

        Args:
            sep (str, optional): Used to join strings. Defaults to the separator used when the part was added, or ' '. Setting this will override the part's separator.
            plaintext (bool, optional): If True, returns a plaintext string. Defaults to False.
            escape_ansi (bool, optional): If True, will escape ANSI codes' \\ → \\\\. Defaults to False.
            fix_punctuation (bool, optional): If True, will fix punctuation spacing. Defaults to SMART_FIX_PUNCTUATION or True.

        Returns:
            str: A rich text string.
        """

        if not self._parts:
            return ""

        attr: StringType = "pln" if plaintext else "esc" if escape_ansi else "fmt"

        return "".join(
            [
                self._get_str(attr, p, np, sep, fix_punctuation)
                for p, np in zip_longest(self._parts, self._parts[1:])
            ]
        )

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

    @property
    def parts(self) -> List["Tinta.Part"]:
        """A list of Tinta.Part objects.

        Returns:
            List[Part]: A list of Tinta.Part objects"""

        return self._parts

    @property
    def has_formatting(self) -> bool:
        """Returns True if any part has formatting.

        Returns:
            bool: True if any part has formatting."""
        return any(p.has_formatting for p in self._parts)

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

        fg: Union[int, None] = 0
        if isinstance(self.color, int):
            fg = self.color
        elif isinstance(self.color, str):
            fg = self.colors.get(self.color or "default")

        if not self.has_formatting and fg == 0:
            # We don't want to add an ansi reset code if we're not adding any formatting
            fg = None

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

    @overload
    def tint(self, *s: Any, color: Union[str, int], sep: str = SEP) -> "Tinta": ...

    @overload
    def tint(self, color: Union[str, int], *s: Any, sep: str = SEP) -> "Tinta": ...

    # pylint: disable=redefined-outer-name
    def tint(self, *args, **kwargs) -> "Tinta":
        """Adds segments of text colored with the specified color.
        Can be used in place of calling named color methods.

        Args:
            color (str | int, optional): A color name or ANSI color index. Defaults to first argument.
            *s: Any: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """

        return tint(self, *args, **kwargs)

    @overload
    def inspect(self, code: int, name: None = None, throw: bool = False) -> str: ...

    @overload
    def inspect(
        self, code: None = None, name: str = "default", throw: bool = False
    ) -> int: ...

    def inspect(
        self,
        code: Optional[int] = None,
        name: Optional[str] = None,
        throw: bool = False,
    ) -> Union[str, int, None]:
        """Queries the known colors by code or name, and returns the corresponding name or code, respectively.

        Args:
            code (int, optional): An ANSI color code. Defaults to None.
            name (str, optional): A color name. Defaults to None.

        Returns:
            Union[str, int]: A color name or code, if found, otherwise None.
        """

        if code is not None and name is not None:
            raise AttributeError(
                "Tinta.inspect() accepts either a code or a name, not both."
            )

        try:
            if code is not None:
                if code == 0:
                    return "default"
                return self.colors.reverse_get(code)

            elif name is not None:
                if name == "default":
                    return 0
                return self.colors.get(name)
        except MissingColorError as e:
            if throw:
                raise e
        return None

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

    @deprecated("Use clear() instead.")
    def reset(self, *s: Any, sep: str = SEP) -> "Tinta":
        return self.push(*s, sep=sep)

    @deprecated("Use nl() instead.")
    def line(self, *s, sep: str = SEP) -> "Tinta":
        return self.nl(*s, sep=sep)

    def nl(self, *s, sep: str = SEP) -> "Tinta":
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
        if STEALTH and not force:
            return

        use_plaintext = True if plaintext or PREFER_PLAINTEXT else False
        s = self.to_str(sep=sep, plaintext=use_plaintext)
        # if s.strip() does not end with reset, add it after the last non-whitespace character
        if not use_plaintext and not was_reset(s):
            s = ensure_reset(s)
        print(
            self.to_str(sep=sep, plaintext=use_plaintext),
            end=end,
            file=file,
            flush=flush,
        )

        self.clear()
        self._parts = []

    def __getattr__(self, name: str) -> "Tinta":
        """Returns a tinted segment of text.

        Args:
            name (str): Name of the color.

        Returns:
            Tinta: A Tinta instance.
        """

        if not name.startswith("_"):
            if hasattr(self.colors, name):
                return cast("Tinta", self.tint(color=name))

            else:
                try:
                    return self.__getattribute__(name)  # type: ignore
                except AttributeError as e:
                    known_colors = "\n - ".join(self.colors.list_colors())
                    known_colors = f" - {known_colors}"
                    raise AttributeError(
                        f"Attribute '{name}' not found. Did you try and access a color that doesn't exist? Available colors:\n{known_colors}"
                    ) from e

        return self.__getattribute__(name)  # type: ignore

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

        def __eq__(self, other) -> bool:
            if not isinstance(other, Tinta.Part):
                return False
            return self.fmt == other.fmt and self.pln == other.pln

        @property
        def esc(self):
            return esc(self.fmt)

        @property
        def has_formatting(self) -> bool:
            return self.fmt != self.pln

    @staticmethod
    def strip_ansi(s: str) -> str:
        """A utility method that strips ANSI escape codes from a string, converting a styled string into plaintext."""
        return re.sub(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", s, re.I | re.M | re.U
        )

    @classmethod
    def ljust(cls, s: str, width: int, fillchar: str = " ") -> str:
        """Returns a string left justified in a field of a specified width, accounting for ansi formatting."""
        chars_to_add = width - len(cls.strip_ansi(s))
        return f"{s}{str(fillchar or '') * chars_to_add}"

    @classmethod
    def rjust(cls, s: str, width: int, fillchar: str = " ") -> str:
        """Returns a string right justified in a field of a specified width, accounting for ansi formatting."""
        chars_to_add = width - len(cls.strip_ansi(s))
        return f"{str(fillchar or '') * chars_to_add}{s}"


def esc(string: str, replace: bool = False) -> str:
    """Returns the raw representation of a string. If replace is true,
    replace a double backslash with a single backslash."""
    r = repr(string)[1:-1]  # Strip the quotes from representation
    if replace:
        r = r.replace("\\\\", "\\")
    return r
