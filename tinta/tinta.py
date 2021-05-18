#!/usr/bin/env python

# Tinta
# Copyright 2021 github.com/brandoncript

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

import os, sys, re
from pathlib import Path

from colors import color
import yaml

class Tinta(object):
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
        parts (list):               A list of richly styled text segments.
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

    def __init__(self, *s, sep=None):
        """Main intializer for Tinta

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.
        """
        
        self.color = 'white'
        self.style = []
        self.parts = []
        self.parts_plaintext = []
        self.sep = self._sep(sep)
        self._prefixes = []

        # Inject ANSI helper functions
        for c in vars(self.ansi):
            self._colorizer(c)

        if s:
            self.add(*s, sep=self._sep(sep))

    def __repr__(self) -> str:
        """Generates a string representation of the current 
        Tinta instance.

        Returns:
            str: Plaintext string
        """
        return str(self.plaintext())

    def _colorizer(self, c: str):
        """Generates statically typed color methods 
        based on colors.yaml.

        Args:
            c (str): Method name of color, e.g. 'pink', 'blue'.
        """
        def add(*s, sep=None):
            if c is not None:
                self.color = c
            self.add(*s, sep=self._sep(sep))
            return self
        self.__setattr__(c, add)
    
    def text(self, sep=None) -> str:
        """Returns a compiled rich text string, joined by 'sep'.

        Args:
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            str: A rich text string.
        """
        return self._sep(sep).join(self.parts)

    def plaintext(self, sep=None) -> str:
        """Returns a compiled plaintext string, joined by 'sep'.

        Args:
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            str: A plaintext string.
        """
        return self._sep(sep).join(self.parts_plaintext)

    def add(self, *s, sep=None) -> 'self':
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
            
        # Join all s parts with the specified separator
        p = self._sep(sep).join([str(x) for x in s])
        
        # Set plaintext
        self.parts_plaintext.extend(to_plaintext(p))
        
        # Collect any prefixes that may have been set
        if self._prefixes:
            p = ''.join(self._prefixes) + p
            self._prefixes = []
        
        # Generate style string
        style = '+'.join(list(set(self.style))) if self.style else None
        
        # Generate formatted string
        fmt = color(p,
                    fg=self.color
                    if type(self.color) == int
                    else getattr(self.ansi, self.color or 'white'),
                    style=style)
        
        # Set formatted text
        self.parts.append(fmt)
        
        return self

    def code(self, *s, code: int = 0, sep=None) -> 'self':
        """Adds segments of text colored with the specified ANSI code.

        Args:
            *s: Segments of text to add.
            code (int, optional): An ANSI code. Defaults to 0.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self.color = int(code)
        self.add(*s, sep=self._sep(sep))
        return self

    def bold(self, *s, sep=None) -> 'self':
        """Adds bold segments to this Tinta instance

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self.style.append('bold')
        self.add(*s, sep=self._sep(sep))
        return self

    def underline(self, *s, sep=None) -> 'self':
        """Adds underline segments to this Tinta instance

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self.style.append('underline')
        self.add(*s, sep=self._sep(sep))
        return self

    def dim(self, *s, sep=None) -> 'self':
        """Adds darker (dimmed) segments to this Tinta instance

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self.style.append('faint')
        self.add(*s, sep=self._sep(sep))
        return self

    def normal(self, *s, sep=None) -> 'self':
        """Removes all styles, then adds segments to this Tinta instance

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self.style = []
        self._prefixes.append('\033[24m\033[21m')
        self.add(*s, sep=self._sep(sep))
        return self

    def reset(self, *s, sep=None) -> 'self':
        """Removes all styles and colors, then adds segments to this 
        Tinta instance

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self.color = None
        self.normal(*s, sep=self._sep(sep))
        return self
    
    def line(self, *s, sep=None) -> 'self':
        """Adds segments to this Tinta instance, preceded by a new line.

        Args:
            *s: Segments of text to add.
            sep (str, optional): Used to join strings. Defaults to ' '.

        Returns:
            self
        """
        self._prefixes = os.linesep
        self.add(*s, sep=self._sep(sep))
        return self
    
    def _sep(self, sep=None) -> str:
        """Returns an appropriate separator for the given sep arg.

        Args:
            sep (str, optional): Separator. Defaults to None.

        Returns:
            str: Separator to use.
        """
        if sep is None:
            if os.environ.get('TINTA_SEPARATOR') is not None:
                self.sep = os.environ.get('TINTA_SEPARATOR')
            else:
                self.sep = ' '
        else:
            self.sep = sep        
        return self.sep

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
        
        if plaintext or os.environ.get('TINTA_PLAINTEXT') is not None:
            print(self.plaintext(self._sep(sep)), end=end, file=file, flush=flush)
            
        else:
            print(self.text(self._sep(sep)), end=end, file=file, flush=flush)
        
        self.reset()
        self.parts = []
        self.parts_plaintext = []
        print('\033[0m', end='')
            
    @staticmethod
    def discover():
        """Prints all 256 colors in a matrix on your system."""
        print('\n')
        for i in range(0, 16):
            for j in range(0, 16):
                code = str(i * 16 + j)
                sys.stdout.write(
                    u"\u001b[38;5;" + code + "m " + code.ljust(4))
            print(u"\u001b[0m")
            
    @classmethod
    def load_colors(cls, path):
        cls.ansi = cls._AnsiColors(path)

    class _AnsiColors:

        """Color builder for Tinta's console output.

        ANSI color map for console output. Get a list of colors here = 
        http://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html#256-colors

        You can change the colors the terminal outputs by changing the 
        ANSI values in colors.yaml.
        """

        def __init__(self, path=None):
            path = Path(path) if path else Path(__file__).parent / 'colors.yaml'
            if not path.is_absolute():
                path = Path().cwd() / path
            with open(path, 'r') as f:
                colormap = yaml.safe_load(f)
                for k, v in colormap.items():
                    self.__setattr__(k, v)


Tinta.ansi = Tinta._AnsiColors()

def to_plaintext(*s):
    ansi_escape = re.compile(r'\x1b\[(K|.*?m)', re.I)
    return [re.sub(ansi_escape, '', x) for x in s]
