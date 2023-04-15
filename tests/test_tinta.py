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

import pytest

from tinta import Tinta

"""Begin import shim
Adds the tinta path so we can load the module directly. You won't
need to do this in your project, because the package will have
been installed via pip into the correct modules dir.
"""
import sys
from pathlib import Path

sys.path.append(str(Path().cwd().parent / 'tinta'))

"""End import shim
"""

Tinta.load_colors('examples/colors.ini')


class TestInit:

    def test_init(self):
        assert len(Tinta('initialized').parts) == 1


class TestColors:

    def test_green(self):
        Tinta().green('green').print()

    def test_red(self):
        Tinta().red('red').print()

    def test_blue(self):
        Tinta().blue('Green').print()

    def test_light_blue(self):
        Tinta().light_blue('light_blue').print()

    def test_yellow(self):
        Tinta().yellow('yellow').print()

    def test_amber(self):
        Tinta().amber('amber').print()

    def test_olive(self):
        Tinta().olive('olive').print()

    def test_orange(self):
        Tinta().orange('orange').print()

    def test_purple(self):
        Tinta().purple('purple').print()

    def test_pink(self):
        Tinta().pink('pink').print()

    def test_gray(self):
        Tinta().gray('gray').print()

    def test_dark_gray(self):
        Tinta().dark_gray('dark_gray').print()

    def test_light_gray(self):
        Tinta().light_gray('light_gray').print()

    def test_black(self):
        Tinta().black('black').print()

    def test_white(self):
        Tinta().white('white').print()


class TestEdgeCases:

    @pytest.mark.xfail()
    def test_missing_color(self):
        Tinta().sparkle().print()

    def test_print_empty(self):
        Tinta().print()

    def test_print_empty_str(self):
        Tinta('').print()

    def test_print_whitespace(self):
        Tinta(' ').print()

    def test_print_none(self):
        Tinta(None).print()


class TestComplexStructure:

    def test_join(self):
        t = Tinta().add('How long').add('can two people talk about nothing?')
        assert t.plaintext() == 'How long can two people talk about nothing?'

        t = Tinta().add('How long', 'can two people talk about nothing?')
        assert t.plaintext() == 'How long can two people talk about nothing?'

    def test_sep(self):
        t = Tinta('How long', sep='').add(
            'can two people talk about nothing?').add('Hmm?')
        assert t.plaintext(
            sep='') == 'How longcan two people talk about nothing? Hmm?'

        t = Tinta('How long').add('can two people',
                                  'talk about nothing?', sep='')
        assert t.plaintext() == 'How long can two peopletalk about nothing?'

        t = Tinta().pink('A section').add().white().blue(
            'of text', sep='').green(',').add().purple('separated.')
        assert t.plaintext() == 'A section of text, separated.'

    def test_parts(self):
        assert len(Tinta().green('green').red('red').blue('blue').parts) == 3
        assert len(Tinta()
                   .green('green')
                   .underline()
                   .red('red')
                   .blue('blue')
                   .yellow('yellow')
                   .parts_formatted) == 4
        assert len(Tinta()
                   .green('green')
                   .underline()
                   .red('red')
                   .blue('blue')
                   .parts_plaintext) == 3

    def test_f_strings(self):
        dog = 'cat'
        assert (Tinta(f"A {dog} is a human's best friend").plaintext()
                == "A cat is a human's best friend")
        assert Tinta(
            f"A {Tinta().red('hologram').text()} is a human's best friend")
