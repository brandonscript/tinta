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
import time
from pathlib import Path
sys.path.append(str(Path().cwd().parent / 'tinta'))
"""End import shim
"""

from tinta import Tinta
Tinta.load_colors('examples/colors.ini')

# The most basic example we can get.
Tinta("That's a really nice car!").print()

# Prints the entire string in red.
Tinta().red("That's a really nice red car!").print()

# Prints the first half in blue, then the rest in red.
Tinta().blue("That's a cool blue car").red("but not as cool as my red one").print()

# Prints the first few words in green, separated by _*_,
# then the final word in purple.
Tinta().green("Sometimes", "We", "Want", "To",
              "Join", "Words", "Differently",
              sep=' * ').purple('Neat!').print()

# Here we underline a word.
Tinta().gray("It's").underline("really").normal(
    "important to be able to style things.").print()

# Here we tried to print in pink, but used the plaintext arg in print.
# You'll notice we still support Python's multiline \ feature.
Tinta().pink("But it's equally important to be able " \
    "to print things in plaintext, too").print(plaintext=True)

# Let's try some f-strings.
animal = 'Tiger'
Tinta().orange(f"Hey, we support f-strings, too! Raaarrr, said Ms. {animal}.")

# And dimming some text.
Tinta().blue("We can").dim("dim").normal("things").print()

# Things getting out of hand? You can break them up easily in multiple
# lines, without having to fiddle with \.
tint = Tinta()
tint.add('Sometimes we need to')
tint.pink('break up long lines of text')
tint.gray('to make them easier to read.')
tint.line('We can even write to a new line!')
tint.print()

# You could do the same using multiple segments, or ()
Tinta().vanilla('I like ice cream',
                'it comes in all sorts'
                'of great and yummy flavors.').print()

(Tinta().vanilla('I like ice cream')
        .red('especially with cherries on top.').print())

# When you're done printing, Tinta resets itself, but you can still
# reuse the original variable.
tint.add('After a print, Tinta resets itself').green()
tint.line('but you can still use the same initialized version.')
tint.print()

# Using native print()'s built-in end, we can terminate a string
# without a newline.
Tinta('And of course as always,').print(end='')
Tinta(' you can print with end=\'\'').print()

# Not enough colors in config.yaml? Add your own on the fly!
Tinta().code('Did you know, you can',
             'write with ansi codes directly, too?', code=127).print()

# Have some fun with separators.
Tinta('A bird', 'I like birds', sep='; ').add('And also cats', 'and dogs', sep=' ').print(sep='\n')

# You could get really fancy and inject some formatted text in the middle,
# using f-strings.
(Tinta().mint('Fate.')
       .dark_gray('It protects')
       .underline().blue(
           f"fools{Tinta().normal().dark_gray(',').text()}",
           sep=''
        )
       .normal().pink('little children,')
       .dark_gray('and ships named')
       .purple("Enterprise.").print())

# Tinta is also smart about how we join things together. If you join
# several objects together, it collapses repeated whitespace. You
# can also use 'sep' to force sections to collapse.
t = Tinta().pink('A section').add().white().blue(
    'of text', sep='').green(',').add().purple('separated.')
print(t.parts)
t.print()

# And finally, you can use some helper tools to clear the current
# console and move up a line.
Tinta().yellow('Loading...').print()
time.sleep(1)
Tinta.clearline()
Tinta().green('Done').print()
time.sleep(1)
Tinta.up()
Tinta().green('Done :)').print()
