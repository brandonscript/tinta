#!/usr/bin/env python

# Tinta — Copyright (c) 2026 github.com/brandonscript
# Licensed under the MIT License. See LICENSE.

"""Tinta is a magical console output tool with support for printing in beautiful
colors and with rich formatting, like bold and underline. It's so pretty,
it's almost like a unicorn.
"""

import os

from .typ import parse_bool

CURSOR_UP_ONE = "\x1b[1A"
ERASE_LINE = "\x1b[2K"
ANSI_RESET = "\x1b[0m"
ANSI_RESET_OCT = "\033[0m"
SEP = os.getenv("TINTA_SEPARATOR", " ")
STEALTH = parse_bool(os.getenv("TINTA_STEALTH", False))
PREFER_PLAINTEXT = parse_bool(os.getenv("TINTA_PLAINTEXT", False))
SMART_FIX_PUNCTUATION = parse_bool(os.getenv("TINTA_SMART_FIX_PUNCTUATION", True))
PERF_MEASURE = parse_bool(os.getenv("TINTA_PERF_MEASURE", True))

ANSI_COLORS = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")
ANSI_STYLES = (
    "bold",
    "dim",
    "italic",
    "underline",
    "blink",
    "rapid_blink",
    "invert",
    "conceal",
    "strikethrough",
)
ANSI_STYLES_OFF = (
    (("reset", "normal", "clear", 0), 0),
    (("bold", "dim", 1, 2), 22),
    (("italic", 3), 23),
    (("underline", 4), 24),
    (("invert", 7), 27),
    (("strikethrough", 9), 29),
)
PUNC = [".", ",", ";", ":", "!", "?"]
