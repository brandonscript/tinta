#!/usr/bin/env python

# Tinta
# Copyright 2024 github.com/brandoncript

# This program is bound to the Hippocratic License 2.1
# Full text is available here:
# https://firstdonoharm.dev/version/2/1/license

# Further to adherence to the Hippocratic Licenese, permission is hereby
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
import functools
import os
import re
import sys
from pathlib import Path
from typing import cast, Literal, Optional, Self, Union

from colors import color
from typing_extensions import deprecated

from tinta.discover import discover as _discover

config = configparser.ConfigParser()


CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'

class _MetaTinta(type):

    colors: 'Tinta._AnsiColors'

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
        *s (tuple(str)): A sequence of one or more text strings, to be joined together.
        sep (str): Used to join segment strings. Defaults to ' '.

    Attributes:
        color (str, int):           A color string or ansi color code (int),
                                    e.g. 'white' or 42
        style (str):                A style string, e.g. 'bold', 'dim', 'underline'.
                                    Multiple styles are joined with a +
        parts (list):               A list of Part objects.
        parts_formatted (list):     A list of richly styled text segments.
        parts_plaintext (list):     A list of unstyled text segments.

    Methods:
        text() -> str:              Returns a compiled rich text string
        plaintext() -> str:         Returns a compiled plaintext string
        add() -> self:              Adds segments using any previously
                                    defined styles.
        code() -> self:             Adds segments using the specified ansi code.
        bold() -> self:             Sets segments to bold.
        underline() -> self:        Sets segments to underline.
        dim() -> self:              Sets segments to a darker, dimmed color.
        normal() -> self:           Removes all styles.
        reset() -> self:            Removes all styles and colors.
        line() -> self:             Adds segments on a new line.
        print():                    Prints the output of a Tinta instance, then resets.
    """

    def __init__(self, *s: str, sep: Optional[str] = None):
        """Main intializer for Tinta

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.
        """

        self.color: int | str | None = 0 # 0 is the default color for terminals
        self.style: list = []
        self._default_sep: str = self._get_default_sep(sep)
        self._parts: list['Tinta.Part'] = []
        self._prefixes: list = []

        # Inject ANSI helper functions
        for c in vars(self.colors):
            self._colorizer(c)

        if s:
            self.push(*s, sep=self._get_default_sep(sep))

    def __call__(self, *s: str, sep: Optional[str] = None) -> 'Tinta':
        return self.push(*s, sep=sep)

    def __repr__(self) -> str:
        """Generates a string representation of the current
        Tinta instance.

        Returns:
            str: Plaintext string
        """
        return str(self.get_str(plaintext=True))

    def _colorizer(self, c: str):
        """Generates statically typed color methods
        based on colors.ini.

        Args:
            c (str): Method name of color, e.g. 'pink', 'blue'.
        """
        self.__setattr__(c, self.push)

    @deprecated("Use get_str() instead.")
    def get_text(self, sep: Optional[str] = None) -> str:
        """
        Deprecated. Use get_str() instead.

        Args:
            sep (str, optional): Used to join strings. Defaults to ''.

        Returns:
            str: A rich text string.
        """
        return self.get_str(sep=sep or '')

    def get_str(self, sep: str='', plaintext: bool = False) -> str:
        """Returns a compiled rich text string, joined by 'sep'. Note that any separators included with a 
        part will be returned as part of the string - adding a separator here may result in a double separator.

        Args:
            sep (str, optional): Used to join strings. Defaults to ''.

        Returns:
            str: A rich text string.
        """

        self._colorizer('asdf')
        self.asdf()

        attr = 'fmt' if not plaintext else 'pln'

        return sep.join([f'{getattr(part, attr)}{part.sep}' for part in self._parts]).rstrip(
            self._parts[-1].sep) if self._parts else sep

    @property
    def parts(self) -> list['Tinta.Part']:
        """Returns a list of Tinta parts

        Returns:
            list[Part]: A list of Parts."""
        return self._parts

    def get_parts(self, style: Optional[Literal['fmt', 'pln', 'esc', 'Part']]=None) -> Union[list[str], list['Tinta.Part']]:
        """Returns a list of string parts

        Args:
            style (str, optional): The style of the parts to return. Defaults to None. Can be 'fmt', 'pln', or 'esc'.

        Returns:
            list[str] | list[Part]: A list of Parts, or a list of strings if specifying 'style'."""

        if style == 'fmt':
            return [part.fmt for part in self._parts]

        if style == 'pln':
            return [part.pln for part in self._parts]

        if style == 'esc':
            return [part.esc for part in self._parts]

        return self._parts

    @property
    @deprecated("Use parts[style='formatted'] instead.")
    def parts_formatted(self) -> list:
        """Returns a list of richly formated string parts

        Returns:
            str: A list of formatted strings."""
        return [part.fmt for part in self._parts]

    @property
    @deprecated("Use parts[style='formatted'] instead.")
    def parts_plaintext(self) -> list:
        """Returns a list of plaintext string parts

        Returns:
            str: A list of plaintext strings."""
        return [part.pln for part in self._parts]

    @property
    @deprecated("Use parts[style='formatted'] instead.")
    def parts_esc(self) -> list:
        """Returns a list of escaped formatted string parts

        Returns:
            str: A list of esc strings."""
        return [part.esc for part in self._parts]

    @deprecated("Use get_str(plaintext=True) instead.")
    def get_plaintext(self, sep: Optional[str] = None) -> str:
        """Deprecated. Use get_str(plaintext=True) instead.

        Args:
            sep (str, optional): Used to join strings. Defaults to ''.

        Returns:
            str: A plaintext string.
        """
        return self.get_str(sep=sep or '', plaintext=True)


    def push(self, *s: str, sep: Optional[str] = None) -> 'Tinta':
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

        sep = self._get_default_sep(sep)

        # Join all s parts with the specified separator
        p = sep.join([str(x) for x in s])

        # Collect any prefixes that may have been set
        if self._prefixes:
            p = ''.join(self._prefixes) + p
            self._prefixes = []

        # Generate style string
        style = '+'.join(list(set(self.style))) if self.style else None

        # Generate formatted string
        fmt = color(p,
                    fg=self.color
                    if isinstance(self.color, int)
                    else getattr(self.colors, self.color or 'white'),
                    style=style)

        # Append to parts list
        self._parts.append(Tinta.Part(fmt, p, sep))

        return self


    @deprecated("Use push() or just __call__() (e.g. Tinta('text')('more text')) instead.")
    def add(self, *s: str, sep: Optional[str] = None) -> 'Tinta':
        """Deprecated. Use push() or just __call__() (e.g. Tinta('text')('more text')) instead.

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        return self.push(*s, sep=sep)

    @functools.wraps(push)
    def _(self, *s: str, sep: Optional[str] = None) -> 'Tinta':
        return self.push(*s, sep=sep)


    def pop(self, qty: int = 1) -> 'Tinta':
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
    def remove(self, qty: int = 1) -> 'Tinta':
        return self.pop(qty)

    # pylint: disable=redefined-outer-name
    def tint(self, color: Optional[str | int] = None, *s: str, sep: str | None=None) -> 'Tinta':
        """Adds segments of text colored with the specified color.
        Can be used in place of calling named color methods.

        Args:
            color (str | int, optional): A color name or ANSI color index. Defaults to first argument.
            *s: str: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """

        if not color:
            if not len(s) > 1:
                raise AttributeError(
                    'If no color is specified, tint() requires at least two arguments.')

            color = s[0]
            s = s[1:]

        # if color is numeric integer string, assume it's an ANSI color code
        if isinstance(color, str) and color.isdigit():
            color = int(color)

        # Check if color_name is a valid color if color is a string
        if isinstance(color, str) and not hasattr(self.colors, color):  # type: ignore
            raise AttributeError(
                f'Invalid color name: {color}. Is it in colors.ini?')

        self.color = color
        self.push(*s, sep=self._get_default_sep(sep))
        return self

    @deprecated("Use tint() instead, setting color=<int:A valid ANSI color code>.")
    def code(self, code: int = 0, *s: str, sep: Optional[str]=None) -> 'Tinta':
        """Adds segments of text colored with the specified ANSI code.

        Args:
            *s: Segments of text to add.
            code (int, optional): An ANSI code. Defaults to 0.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self.color = int(code)
        self.push(*s, sep=self._get_default_sep(sep))
        return self

    def bold(self, *s: str, sep: Optional[str]=None) -> 'Tinta':
        """Adds bold segments to this Tinta instance

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self.style.append('bold')
        self.push(*s, sep=self._get_default_sep(sep))
        return self

    def underline(self, *s: str, sep: Optional[str]=None) -> 'Tinta':
        """Adds underline segments to this Tinta instance

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self.style.append('underline')
        self.push(*s, sep=self._get_default_sep(sep))
        return self

    def dim(self, *s: str, sep: Optional[str]=None) -> 'Tinta':
        """Adds darker (dimmed) segments to this Tinta instance

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self.style.append('faint')
        self.push(*s, sep=self._get_default_sep(sep))
        return self

    def normal(self, *s: str, sep: Optional[str]=None) -> 'Tinta':
        """Removes all styles, then adds segments to this Tinta instance

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self.style = []
        # self._prefixes.append('\033[24m\033[21m')
        self.push(*s, sep=self._get_default_sep(sep))
        return self

    def reset(self, *s: str, sep: Optional[str]=None) -> 'Tinta':
        """Removes all styles and colors, then adds segments to this
        Tinta instance

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self.color = None
        self.normal(*s, sep=self._get_default_sep(sep))
        return self

    @functools.wraps(reset)
    def clear(self, *s: str, sep: Optional[str]=None) -> 'Tinta':
        return self.reset(*s, sep=sep)

    def line(self, *s, sep=None) -> 'Tinta':
        """Adds segments to this Tinta instance, preceded by a new line.

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self._prefixes = [os.linesep]
        self.push(*s, sep=self._get_default_sep(sep))
        return self

    def _get_default_sep(self, sep: Optional[str]=None) -> str:
        """Returns an appropriate separator for the given sep arg.

        Args:
            sep (str, optional): Separator. Defaults to None.

        Returns:
            str: Separator to use.
        """
        if sep is None:
            sep = str(os.environ.get('TINTA_SEPARATOR', ' '))
        return sep

    def print(self, sep=None, end='\n', file=sys.stdout,
              flush=False, plaintext=False, force=False):
        """Prints a Tinta composite to the console. Once printed,
        this Tinta instance is cleared of all configuration, but can
        can continue to be used to print.

        Env: These environment variables, when set, affect Tinta globally.
            TINTA_STEALTH (not None): Hides all console output. Can be
                                      overridden by 'force'.
            TINTA_PLAINTEXT (not None): Prints all output in plaintext.

        Args:
            sep (str, optional): Used to join strings. Defaults to ' '.
            end (str, optional): String terminator. Defaults to '\n'.
            file (optional): File to write to. Defaults to sys.stdout.
            flush (bool, optional): Clears the current console line.
            plaintext (bool, optional): Prints in plaintext. Defaults to False.
            force (bool, option): Forces printing, overriding TINTA_STEALTH.
        """
        # We don't print if the TINTA_STEALTH env is set
        if os.environ.get('TINTA_STEALTH') is not None:
            return

        use_plaintext = True if plaintext or os.environ.get('TINTA_PLAINTEXT') is not None else False
        print(self.get_str(sep=self._get_default_sep(sep), plaintext=use_plaintext), end=end, file=file, flush=flush)

        self.reset()
        self._parts = []
        print('\033[0m', end='', file=file, flush=flush)


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
                    raise AttributeError(f"Attribute '{name}' not found. Did you try and access a color that doesn't exist? Available colors:\n{known_colors}") from e

        return self.__getattribute__(name)

    @staticmethod
    def discover(background=False):
        """Prints all 256 colors in a matrix on your system. If background is True,
        it will print background colors with numbers on top."""
        _discover(background)

    @staticmethod
    def clearline():
        """Clears the current printed line.
        """

        if sys.stdout:
            sys.stdout.write(CURSOR_UP_ONE)
            sys.stdout.write(ERASE_LINE)
            sys.stdout.flush()

    @staticmethod
    def up():
        """Moves up to the previous line.
        """

        if sys.stdout:
            sys.stdout.write(CURSOR_UP_ONE)
            sys.stdout.flush()

    @classmethod
    def load_colors(cls, path: str | Path):
        loaded_colors = cls._AnsiColors(path)

        # Check if any of the color names loaded match the built-in methods. If so, raise an error.
        for col in loaded_colors.list_colors():
            if hasattr(cls, col):
                raise AttributeError(
                    f"Cannot overwrite built-in method '\
                        {col}' with color name. Please rename the color in '{path}'.")

        # Add the loaded colors to the Tinta class
        cls.colors = loaded_colors

    class Part:
        """A segment part of text, intended to be joined together
        for a print statement.

        Args:
            fmt (str):      A formatted string of text.
            p (str):        A plaintext representation of fmt.
            sep (str):      Used to join segment strings. Defaults to ' '.
        """

        def __init__(self, fmt: str, pln: str, sep: Optional[str] = None):
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

    class _AnsiColors:

        """Color builder for Tinta's console output.

        ANSI color map for console output. Get a list of colors here =
        http://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html#256-colors

        Or run Tinta.discover() to see all 256 colors on your system.

        You can change the colors the terminal outputs by changing the
        ANSI values in colors.ini.
        """

        def __init__(self, path: str | Path | None = None):
            path = Path(path) if path else Path(__file__).parent / 'colors.ini'
            if not path.is_absolute():
                path = Path().cwd() / path
            if not path.exists():
                raise FileNotFoundError(
                    f"Tinta failed to load colors, '{path}' does not exist.")

            # if path is a dir, look for colors.ini
            if path.is_dir():
                path = path / 'colors.ini'

            # if there is still no colors.ini file, look for one in Path.cwd() or PYTHONPATH
            if not path.exists():
                for p in [Path().cwd(), Path(sys.path[0])]:
                    if (p / 'colors.ini').exists():
                        path = p / 'colors.ini'
                        break

            if not path.exists():
                raise FileNotFoundError(
                    f"Tinta failed to load colors, could not find 'colors.ini' in cwd or in PYTHONPATH. Please provide a valid path to a colors.ini file.")

            config.read(path)
            for k, v in config['colors'].items():
                self.__setattr__(k, int(v))

        def list_colors(self):
            """Returns a list of all colors in the colors.ini file.
            """
            return list(config['colors'].keys())


Tinta.colors = Tinta._AnsiColors()


def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)


def esc(string: str, replace: bool = False) -> str:
    """Returns the raw representation of a string. If replace is true, 
    replace a double backslash with a single backslash."""
    r = repr(string)[1:-1]  # Strip the quotes from representation
    if replace:
        r = r.replace('\\\\', '\\')
    return r
