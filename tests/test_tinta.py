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


from typing import List, Tuple

import pytest

# pylint: disable=import-error
from tinta import Tinta

Tinta.load_colors("examples/colors.ini")


class TestInit:

    def test_init(self):
        assert len(Tinta("initialized").parts) == 1


class TestColors:

    def test_green(self):
        Tinta().green("green").print()

    def test_red(self):
        Tinta().red("red").print()

    def test_blue(self):
        Tinta().blue("Green").print()

    def test_light_blue(self):
        Tinta().light_blue("light_blue").print()

    def test_yellow(self):
        Tinta().yellow("yellow").print()

    def test_amber(self):
        Tinta().amber("amber").print()

    def test_olive(self):
        Tinta().olive("olive").print()

    def test_orange(self):
        Tinta().orange("orange").print()

    def test_purple(self):
        Tinta().purple("purple").print()

    def test_pink(self):
        Tinta().pink("pink").print()

    def test_gray(self):
        Tinta().gray("gray").print()

    def test_dark_gray(self):
        Tinta().dark_gray("dark_gray").print()

    def test_light_gray(self):
        Tinta().light_gray("light_gray").print()

    def test_black(self):
        Tinta().black("black").print()

    def test_white(self):
        Tinta().white("white").print()


class TestLowerLevel:

    ITS_NOT_EASY = "it's not easy being green"

    def assert_its_not_easy_being_green(self, out: str):
        assert self.ITS_NOT_EASY in out
        assert "\x1b[38;5;35m" in out

    def test_tint_takes_int_arg0_as_color(self):
        out = Tinta().tint(35, self.ITS_NOT_EASY).to_str()
        self.assert_its_not_easy_being_green(out)

    def test_tint_takes_str_arg0_as_color(self):
        out = Tinta().tint("green", self.ITS_NOT_EASY).to_str()
        self.assert_its_not_easy_being_green(out)

    def test_tint_takes_int_color_kwarg(self):
        out = Tinta().tint(self.ITS_NOT_EASY, color=35).to_str()
        self.assert_its_not_easy_being_green(out)

    def test_tint_takes_str_color_kwarg(self):
        out = Tinta().tint(self.ITS_NOT_EASY, color="green").to_str()
        self.assert_its_not_easy_being_green(out)


class TestEdgeCases:

    @pytest.mark.xfail()
    def test_missing_color(self):
        Tinta().sparkle().print()

    @pytest.mark.xfail()
    def test_color_same_as_builtin_method(self):
        Tinta().load_colors("tests/test_colors_invalid.ini")

    def test_print_empty(self):
        Tinta().print()

    def test_print_empty_str(self):
        Tinta("").print()

    def test_print_whitespace(self):
        Tinta(" ").print()

    def test_print_none(self):
        Tinta(None).print()

    def test_tint_color_0(self):
        Tinta().tint(0, "Zero").print()

    def test_sep_inherits_prev_part_color(self):
        assert (
            Tinta().red("Red").green("Green").blue("Blue").to_str(sep=";")
            == "\x1b[38;5;1mRed;\x1b[38;5;35mGreen;\x1b[38;5;32mBlue\x1b[0m"
        )


class TestFeatures:

    def test_inspect(self):
        assert Tinta().inspect(code=0) == "default"
        assert Tinta().inspect(name="default") == 0

        assert Tinta().inspect(code=35) == "green"
        assert Tinta().inspect(name="green") == 35

    @pytest.mark.parametrize(
        "test,expected",
        [
            ("Hello world", "Hello world"),
            (Tinta("Hello")("world").to_str(), "Hello world"),
            ("Hello  world", "Hello  world"),
            (Tinta("Hello ")("world").to_str(), "Hello  world"),
            ("Hello , world", "Hello , world"),
            (Tinta("Hello")(", world").to_str(), "Hello, world"),
            ("Hello world !", "Hello world !"),
            (Tinta("Hello world")("!").to_str(), "Hello world!"),
            ("Nice .", "Nice ."),
            (Tinta("Nice")(".").to_str(), "Nice."),
            ("Nice .gif file", "Nice .gif file"),
            (Tinta("Nice")(".gif file").to_str(), "Nice .gif file"),
            (" *** Important", " *** Important"),
            (", world", ", world"),
            (" , world", " , world"),
            (Tinta(",")("world").to_str(), ", world"),
            (
                Tinta()
                .red(" *** Important : Smart fix punctuation should work with")
                .green("ANSI")
                .red(", as well as plaintext.")
                .to_str(),
                "\x1b[38;5;1m *** Important : Smart fix punctuation should work with \x1b[38;5;35mANSI\x1b[38;5;1m, as well as plaintext.\x1b[0m",
            ),
        ],
    )
    def test_smart_fix_punctuation(self, test: str, expected: str):
        assert Tinta(test).to_str() == expected


class TestComplexStructure:

    @pytest.mark.parametrize(
        "inputs,expected",
        [
            (
                ("How long", "can two people talk about nothing?"),
                "How long can two people talk about nothing?",
            ),
            (
                (["How long", "can two people talk about nothing?"]),
                "How long can two people talk about nothing?",
            ),
        ],
    )
    def test_push(self, inputs: Tuple[str], expected):
        t = Tinta().push(*inputs)
        assert t.get_plaintext() == expected
        assert t.to_str(plaintext=True) == expected

    @pytest.mark.parametrize(
        "inputs,expected",
        [
            (
                (
                    [
                        ("How long", None),
                        ("can two people talk about nothing?", None),
                        ("Hmm?", None),
                    ],
                    "How long can two people talk about nothing? Hmm?",
                )
            ),
            (
                (
                    [
                        ("How long", ""),
                        ("can two people talk about nothing?", ""),
                        ("Hmm?", ""),
                    ],
                    "How longcan two people talk about nothing?Hmm?",
                )
            ),
            (
                (
                    [
                        ("How long", " "),
                        ("can two people", " "),
                        ("talk about nothing?", " "),
                    ],
                    "How long can two people talk about nothing?",
                )
            ),
            (
                (
                    [("A section", " "), ("of text", ""), (", separated.", " ")],
                    "A section of text, separated.",
                )
            ),
        ],
    )
    def test_sep(self, inputs: List[Tuple[str, str]], expected: str) -> None:
        t = Tinta()
        for s, sep in inputs:
            t.push(s, sep=sep)
        assert t.get_plaintext() == expected
        assert t.to_str(plaintext=True) == expected

    def testparts(self):
        assert len(Tinta().green("green").red("red").blue("blue").parts) == 3
        assert (
            len(
                Tinta()
                .green("green")
                .underline()
                .red("red")
                .blue("blue")
                .yellow("yellow")
                .parts_fmt
            )
            == 4
        )
        assert (
            len(Tinta().green("green").underline().red("red").blue("blue").parts_pln)
            == 3
        )

    def test_f_strings(self):
        dog = "cat"
        assert (
            Tinta(f"A {dog} is a human's best friend").get_plaintext()
            == "A cat is a human's best friend"
        )
        assert Tinta(f"A {Tinta().red('hologram').to_str()} is a human's best friend")

    def test_push(self):
        t = Tinta().push("How long").push("can two people talk about nothing?")
        assert t.get_plaintext() == "How long can two people talk about nothing?"

        assert len(t.parts) == 2
        assert len(t.parts_fmt) == 2
        assert len(t.parts_pln) == 2

        t = Tinta().push("How long", "can two people talk about nothing?")
        assert t.get_plaintext() == "How long can two people talk about nothing?"

        assert len(t.parts) == 1
        assert len(t.parts_fmt) == 1
        assert len(t.parts_pln) == 1

    def test_pop(self):
        t = Tinta().push("How long").push("can two people talk about nothing?")
        t.pop()
        assert t.get_plaintext() == "How long"
        assert len(t.parts) == 1
        assert len(t.parts_fmt) == 1
        assert len(t.parts_pln) == 1

        t = Tinta()
        for p in range(10):
            t.push(str(p))

        assert len(t.parts) == 10
        t.pop(10)

        assert len(t.parts) == 0

        t.remove(2)  # Shouldn't error if we remove more than we have

        assert len(t.parts) == 0

    def test_zero_handles_reset(self):
        s = (
            Tinta("White")
            .red("Red")
            .green("Green")
            .blue("Blue")
            .tint(0, "Reset")
            .to_str(sep=" ")
        )
        print(s)
        assert (
            s
            == "White \x1b[38;5;1mRed \x1b[38;5;35mGreen \x1b[38;5;32mBlue \x1b[0mReset\x1b[0m"
        )
