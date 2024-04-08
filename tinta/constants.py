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
