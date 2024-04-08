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
from pathlib import Path
from typing import Any, List, Optional, overload, Sequence, Union

from .ansi import AnsiColors
from .constants import (
    ANSI_STYLES,
    CURSOR_UP_ONE,
    ERASE_LINE,
    PREFER_PLAINTEXT,
    PUNC,
    SEP,
    SMART_FIX_PUNCTUATION,
    STEALTH,
)
from .discover import discover as _discover
from .stylize import _join, ensure_reset, is_ansi_str, stylize, tint
from .typ import copy_kwargs, MissingColorError, StringType

config = configparser.ConfigParser()


class _MetaTinta(type):

    _initialized = False
    _colors: AnsiColors

    def __init__(cls, name, bases, dct):
        super(_MetaTinta, cls).__init__(name, bases, dct)

        if not cls._initialized:
            cls._colors = AnsiColors()
            cls._initialized = True

    def load_colors(cls, path: Union[str, Path]):
        AnsiColors._initialized = False
        cls._colors = AnsiColors(path)


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
        bold() -> self:             Sets segments to bold.
        underline() -> self:        Sets segments to underline.
        dim() -> self:              Sets segments to a darker, dimmed color.
        strikethrough() -> self:    Sets segments to strikethrough.
        normal() -> self:           Removes all styles.
        clear() -> self:            Removes all styles and colors.
        line() -> self:             Adds segments on a new line.
        print():                    Prints the output of a Tinta instance, then clears.
    """

    def __init__(
        self,
        *s: Any,
        color: Union[str, int] = 0,
        styles: List[str] = [],
        sep: str = SEP,
    ):
        """Main intializer for Tinta

        Args:
            *s: Segments of text to add.
            color (Union[str, int], optional): A color name or ANSI color index. Defaults to None.
            styles (List[str], optional): A list of style strings. Defaults to None.
            sep (str, optional): Used to join strings. Defaults to ' '.
        """

        self._styler = Tinta.Styler(color=color, styles=styles)
        self._parts: List["Tinta.Part"] = []
        self._prefixes: List[str] = []

        # Inject ANSI helper functions
        for c in Tinta._colors.color_dict:
            if hasattr(self, c) and not str(getattr(self, c)).startswith(
                "functools.partial(<bound method Tinta.tint"
            ):
                raise AttributeError(
                    f"Cannot overwrite built-in method '{c}' with color name. Please rename the color in '{Tinta._colors._colors_ini_path}'."
                )
            setattr(self, c, functools.partial(self.tint, color=c))

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
        mp: "Tinta.Part",
        np: Optional["Tinta.Part"],
        sep: Optional[str],
    ) -> str:
        if not np:
            return ""
        return sep if sep is not None else mp.sep

    def _get_str(
        self,
        attr: StringType,
        lp: Optional["Tinta.Part"],
        mp: "Tinta.Part",
        np: Optional["Tinta.Part"],
        sep: Optional[str] = None,
        fix_punc: bool = SMART_FIX_PUNCTUATION,
    ) -> str:

        s: str = (
            mp.pln
            if attr == "pln"
            else mp.fmt(lp, np) if attr == "fmt" else mp.esc(lp, np)
        )

        if fix_punc:
            # next char is empty
            if not np or not np.pln:
                return s

            # current char is empty
            if not mp.pln:
                return s

            # next or last char is newline
            if np.pln.startswith(os.linesep) or mp.pln.endswith(os.linesep):
                return s

            # next char is punctuation and affects the separator
            if np.pln[0] in PUNC and (len(np.pln) == 1 or np.pln[1] == " "):
                return s

        return f"{s}{self._get_sep(mp, np, sep)}"

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
                self._get_str(attr, lp, p, np, sep, fix_punctuation)
                for lp, p, np in self._parts_tuple
            ]
        )

    @property
    def color(self) -> str:
        """A color string, e.g. 'white' or 'blue'.

        Returns:
            str: A color string or ansi color code (int)."""
        return self._styler.color

    def set_color(self, value: Union[int, str]):
        """Sets the current color of the Tinta instance.

        Args:
            value (Union[int, str]): A color string or ansi color code (int),
            e.g. 'white' or 42.
        """

        self._styler.set_color(value)

    @property
    def color_code(self) -> int:
        """The ANSI code for the current color.

        Returns:
            int: The ANSI code for the current color."""
        return self._styler.color_code or 0

    @property
    def style(self) -> List[str]:
        """A style string, e.g. 'bold', 'dim', 'underline'.

        Returns:
            List[str]: A list of style strings."""
        return self._styler.active_styles or []

    @style.setter
    def style(self, value: Union[Sequence[str], Sequence[int]]):
        self._styler.set_styles(value)

    @property
    def parts(self) -> List["Tinta.Part"]:
        """A list of Tinta.Part objects.

        Returns:
            List[Part]: A list of Tinta.Part objects"""

        return self._parts

    @property
    def _parts_tuple(self):

        for i, p in enumerate(self._parts):
            lp = self._parts[i - 1] if i > 0 else None
            np = self._parts[i + 1] if i < len(self._parts) - 1 else None
            yield lp, p, np

    @property
    def current_part(self) -> "Tinta.Part":
        if not self._parts:
            self._parts.append(Tinta.Part("", Tinta.Styler(), sep=SEP))
        return self._parts[-1]

    @property
    def has_formatting(self) -> bool:
        """Returns True if any part has formatting.

        Returns:
            bool: True if any part has formatting."""
        return bool(next((p.has_formatting for p in self._parts), False))

    @property
    def parts_fmt(self) -> list:
        """Returns a list of richly formated string parts

        Returns:
            str: A list of formatted strings."""
        return [p.fmt(lp, np) for lp, p, np in self._parts_tuple]

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
        return [p.esc(lp, np) for lp, p, np in self._parts_tuple]

    def push(
        self,
        *s: Any,
        sep: Optional[str] = SEP,
    ) -> "Tinta":
        """Adds segments to this Tinta instance

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """

        # If an empty set of segments is passed, skip to the
        # next segment (to prevent duplicating whitespace).
        # if not s:
        #     return self

        if sep is None:
            sep = SEP

        # Join all s parts with the specified separator
        pln = "" if not s else sep.join([str(x) for x in s])

        # Collect any prefixes that may have been set
        if self._prefixes:
            pln = "".join(self._prefixes) + pln
            self._prefixes = []

        # TODO: Add support for background colors

        # If the current part's string is not empty, add a new part
        if self.current_part.s:
            self._parts.append(Tinta.Part(pln, self._styler.copy(), sep=sep))

        # Otherwise, update the current part with additional styles and current string
        elif not self.current_part.s:
            self.current_part.s = pln
            self.current_part.styler = self._styler.copy()
            self.current_part.sep = sep

        self._styler._force_clear = False

        return self

    def pop(self, qty: int = 1) -> "Tinta":
        """Removes the last 'qty' segments from this Tinta instance

        Args:
            qty (int, optional): Number of segments to remove. Defaults to 1.

        Returns:
            self
        """
        for _ in range(min(qty, len(self._parts))):
            self._parts.pop()
        self._styler = self._parts[-1].styler.copy() if self._parts else Tinta.Styler()
        return self

    @overload
    def tint(self, *s: Any, color: Union[str, int], sep: str = SEP) -> "Tinta": ...

    @overload
    def tint(self, color: Union[str, int], *s: Any, sep: str = SEP) -> "Tinta": ...

    def tint(self, *args, **kwargs) -> "Tinta":
        """Adds segments of text colored with the specified color.
        Can be used in place of calling named color methods.

        Args:
            instance (Tinta): The Tinta instance.
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
                return self._colors.reverse_get(code)

            elif name is not None:
                if name == "default":
                    return 0
                return self._colors.get(name)
        except MissingColorError as e:
            if throw:
                raise e
        return None

    def bold(self, *s: Any, sep: str = SEP) -> "Tinta":
        """Adds bold segments to this Tinta instance

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self._styler.toggle_styles("bold")
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
        self._styler.toggle_styles("underline")
        self.push(*s, sep=sep)
        return self

    @copy_kwargs(underline)
    def u(self, *args, **kwargs):
        return self.underline(*args, **kwargs)

    @copy_kwargs(underline)
    def _(self, *args, **kwargs):
        return self.underline(*args, **kwargs)

    def strikethrough(self, *s: Any, sep: str = SEP) -> "Tinta":
        """Adds strikethrough segments to this Tinta instance

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self._styler.toggle_styles("strikethrough")
        self.push(*s, sep=sep)
        return self

    def dim(self, *s: Any, sep: str = SEP) -> "Tinta":
        """Adds darker (dimmed) segments to this Tinta instance

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self._styler.toggle_styles("dim")
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
        # self._prefixes.append('\033[24m\033[21m')
        self._styler.clear_styles()
        self.push(*s, sep=sep)
        return self

    def default(self, *s: Any, sep: str = SEP) -> "Tinta":
        """Removes all styles, then adds segments to this Tinta instance

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        # self._prefixes.append('\033[24m\033[21m')
        self.set_color(0)
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
        self._styler.clear_all(force=True)
        self.push(*s, sep=sep)
        # self._prefixes.append('\033[24m\033[21m')
        return self

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
        if not use_plaintext:
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
            # if hasattr(self.colors, name):
            #     return cast("Tinta", self.tint(color=name))

            # else:
            try:
                return self.__getattribute__(name)  # type: ignore
            except AttributeError as e:
                known_colors = "\n - ".join(self._colors.color_list)
                known_colors = f" - {known_colors}"
                raise AttributeError(
                    f"'{name}' not found.\nDid you try and access a color that doesn't exist? Available colors:\n{known_colors}\n"
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

    class Styler:
        """A class to hold format and style config for a Tinta part."""

        color: str = "default"
        color_code: int = 0
        bold: bool = False
        dim: bool = False
        italic: bool = False
        underline: bool = False
        blink: bool = False
        rapid_blink: bool = False
        invert: bool = False
        conceal: bool = False
        strikethrough: bool = False
        _force_clear: bool = False

        def __init__(
            self,
            *,
            color: Union[str, int] = 0,
            styles: List[str] = [],
            force_clear=False,
        ):

            self.set_color(color)
            self.set_styles(styles)
            self._force_clear = force_clear

        def __repr__(self):
            color_str = f"{self.color}{{{self.color_code}}}"
            if not self.active_styles:
                return color_str
            if not any([self.color, self.active_styles]):
                return "(plain)"
            return " - ".join([color_str, _join(*self.active_styles)])

        def __str__(self):
            return self.__repr__()

        def __eq__(self, other):
            if not isinstance(other, Tinta.Styler):
                return False
            return (
                self.color == other.color and self.active_styles == other.active_styles
            )

        def copy(self):
            new = self.__new__(self.__class__)
            new.color = self.color
            new.color_code = self.color_code
            for k in ANSI_STYLES:
                setattr(new, k, getattr(self, k))
            return new

        @property
        def active_styles(self) -> List[str]:
            """Returns a list of active styles."""
            return [st for st in ANSI_STYLES if getattr(self, st, None)]

        @property
        def inactive_styles(self) -> List[str]:
            """Returns a list of inactive styles."""
            return [st for st in ANSI_STYLES if not getattr(self, st, None)]

        def set_color(self, color: Union[str, int]):

            if isinstance(color, str):
                code = Tinta._colors.get(color)
                self.color = (
                    Tinta._colors.reverse_get(code, ignore_errors=True)
                    if is_ansi_str(color)
                    else color
                )
                self.color_code = code
            else:
                self.color = Tinta._colors.reverse_get(color, ignore_errors=True)
                self.color_code = color

        def set_styles(self, styles: Union[Sequence[str], Sequence[int]]):

            from .stylize import validate_styles

            styles = validate_styles(*styles)

            for k in styles:
                setattr(self, k, True)

        def enable_styles(self, *styles: str):
            from .stylize import validate_styles

            styles = validate_styles(*styles)
            for style in styles:
                setattr(self, style, True)

        def disable_styles(self, *styles: str):
            from .stylize import validate_styles

            styles = validate_styles(*styles)
            for style in styles:
                setattr(self, style, False)

        def toggle_styles(self, *styles: str):
            from .stylize import validate_styles

            styles = validate_styles(*styles)
            for style in styles:
                setattr(self, style, not getattr(self, style))

        def clear_styles(self):
            for k in ANSI_STYLES:
                setattr(self, k, False)

        def clear_all(self, force: bool = False):
            for k in ANSI_STYLES:
                setattr(self, k, False)
            self.set_color(0)
            self._force_clear = force

    class Part:
        """A segment part of text, intended to be joined together
        for a print statement.

        Args:
            s (str):                    A segment of unstyled text.
            styler: (Tinta.Styler):     A Tinta.Styler object.
            sep (str):                  Used to join segment strings. Defaults to ' '.
        """

        def __init__(
            self,
            s: str,
            styler: "Optional[Tinta.Styler]" = None,
            sep: str = SEP,
        ):
            self.s = s
            self.styler = styler or Tinta.Styler()
            self.sep = sep

        def __str__(self):
            return self.s

        def __repr__(self):
            return self.__str__()

        def __eq__(self, other):
            if not isinstance(other, Tinta.Part):
                return False
            return self.s == other.s

        @property
        def has_formatting(self):
            return bool(self.styler.active_styles or self.styler.color_code)

        @property
        def color(self):
            return self.styler.color

        @property
        def color_code(self):
            return self.styler.color_code

        @property
        def style(self):
            return self.styler.active_styles

        @property
        def pln(self):
            return self.s

        def fmt(self, lp: "Optional[Tinta.Part]", np: "Optional[Tinta.Part]"):
            return stylize(self.s, lp, self, np)

        def esc(self, lp: "Optional[Tinta.Part]", np: "Optional[Tinta.Part]"):
            return esc(self.fmt(lp, np))

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
