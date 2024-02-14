#!/usr/bin/env python

# Tinta
# Copyright 2023 github.com/brandoncript

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

"""Begin import shim
Adds the tinta path so we can load the module directly. You won't
need to do this in your project, because the package will have
been installed via pip into the correct modules dir.
"""
import sys
from pathlib import Path

sys.path.append(str(Path().cwd().parent / 'tinta'))
# pylint: disable=wrong-import-position, wrong-import-order, import-error
from src import Tinta  # noqa: E402

# End import shim

Tinta.load_colors('examples/colors.ini')

# from colors.ini:

# [colors]
# green = 35
# red = 1
# blue = 32
# light_blue = 37
# yellow = 214
# amber = 208
# olive = 106
# orange = 166
# purple = 18
# pink = 197
# gray = 243
# dark_gray = 235
# light_gray = 248
# black = 0
# white = 255
# error = 1
# debug = 160

# get names of colors from colors.ini
colors = []
with open('examples/colors.ini', 'r', encoding='utf-8') as f:
    colors = [line.split('=')[0].strip()
              for line in f.readlines() if '=' in line]

w = 26
GAP = "\n\n"

method = "Tinta().print(\"plain\")".ljust(w)
Tinta(method, " → plain").print(end=GAP)

for col in colors:
    viz = f" → {col}"
    method = f"Tinta().tint(\"{col}\")".ljust(w)
    Tinta().tint(col, method, viz).print()

    t = Tinta()
    func = getattr(t, col)
    method = f"t.{col}(\"{col}\")".ljust(w)
    func(method, viz).print(end=GAP)

w = 30

method = "Tinta().bold(\"bold\")".ljust(w)
Tinta(method, " →").bold("bold").print()

method = "Tinta().underline(\"underline\")".ljust(w)
Tinta(method, " →").underline("underline").print()

# dim
method = "Tinta().dim(\"dim\")".ljust(w)
Tinta(method).dim(" → dim").print(end=GAP)

# chain methods
t = Tinta()
for i, col in enumerate(colors):
    t.tint(col, col, sep="\n" if i % 2 != 0 else " ")
t.print(end=GAP)

# complex formatting
t = Tinta()
t.vanilla("vanilla").bold('bold', sep="\n")
t.reset()
t.mint("mint").underline('underline', sep="\n")
t.reset()
t.olive("olive").dim('dim', sep="\n")

t.print(end=GAP)

# reset
t = Tinta()
t.vanilla("vanilla").bold('bold', sep="\n")
t.reset("plain text", sep="\n")
t.mint("mint").underline('underline', sep="\n")
t.olive("olive inherits underline", sep="\n").dim(
    'dim inherits both', sep="\n")
t.reset("reset clears all", sep="\n")
t.amber("so we can start fresh")

t.print(end=GAP)
