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


from typing import Any, Callable, List, Tuple

import pytest

# pylint: disable=import-error
from tinta import Tinta

Tinta.load_colors("examples/colors.ini")


class TestInit:

    def test_init(self):
        assert len(Tinta("initialized").parts) == 1


class TestBasicColorizing:

    @pytest.mark.parametrize(
        "color,Testa,expected",
        [
            # fmt: off
            ("green", lambda: Tinta().green("green"), "\x1b[38;5;35mgreen\x1b[0m"),
            ("green", lambda: Tinta().tint(35, "green"), "\x1b[38;5;35mgreen\x1b[0m"),
            ("green", lambda: Tinta().tint("green", "green"), "\x1b[38;5;35mgreen\x1b[0m"),
            ("red", lambda: Tinta().red("red"), "\x1b[38;5;1mred\x1b[0m"),
            ("blue", lambda: Tinta().blue("blue"), "\x1b[38;5;32mblue\x1b[0m"),
            ("blue", lambda: Tinta().blue("Green"), "\x1b[38;5;32mGreen\x1b[0m"),
            ("light_blue", lambda: Tinta().light_blue("light_blue"), "\x1b[38;5;37mlight_blue\x1b[0m"),
            ("yellow", lambda: Tinta().yellow("yellow"), "\x1b[38;5;214myellow\x1b[0m"),
            ("amber", lambda: Tinta().amber("amber"), "\x1b[38;5;208mamber\x1b[0m"),
            ("olive", lambda: Tinta().olive("olive"), "\x1b[38;5;106molive\x1b[0m"),
            ("orange", lambda: Tinta().orange("orange"), "\x1b[38;5;166morange\x1b[0m"),
            ("purple", lambda: Tinta().purple("purple"), "\x1b[38;5;18mpurple\x1b[0m"),
            ("pink", lambda: Tinta().pink("pink"), "\x1b[38;5;197mpink\x1b[0m"),
            ("gray", lambda: Tinta().gray("gray"), "\x1b[38;5;243mgray\x1b[0m"),
            ("dark_gray", lambda: Tinta().dark_gray("dark_gray"), "\x1b[38;5;235mdark_gray\x1b[0m"),
            ("light_gray", lambda: Tinta().light_gray("light_gray"), "\x1b[38;5;248mlight_gray\x1b[0m"),
            ("white", lambda: Tinta().white("white"), "\x1b[38;5;255mwhite\x1b[0m"),
            ("mint", lambda: Tinta().mint("Mint"), "\x1b[38;5;84mMint\x1b[0m")
            # fmt: on
        ],
    )
    def test_colors(self, color, Testa, expected):
        Testa().print()
        assert Testa().to_str() == expected


class TestChaining:

    @pytest.mark.parametrize(
        "test_case, kwargs, expected",
        [
            # fmt: off
            (Tinta().green("green").red("red").blue("blue"), {"sep":"", "plaintext":True}, "greenredblue"),
            (Tinta().green("green").red("red").blue("blue"), {"plaintext": True}, "green red blue"),
            (Tinta().green("green").red("red").blue("blue"), {"sep": ""}, "\x1b[38;5;35mgreen\x1b[38;5;1mred\x1b[38;5;32mblue\x1b[0m"),
            (Tinta().green("green").red("red").blue("blue"), {}, "\x1b[38;5;35mgreen \x1b[38;5;1mred \x1b[38;5;32mblue\x1b[0m"),
            # fmt: on
        ],
    )
    def test_chaining_resets_correctly(
        self, test_case: Tinta, kwargs: dict[str, Any], expected: str
    ):
        s = test_case.to_str(**kwargs)
        test_case.print(**kwargs)
        assert s == expected

    @pytest.mark.parametrize(
        "Testa,expected",
        [
            (
                lambda: Tinta().mint("Mint\nice cream"),
                "\x1b[38;5;84mMint\nice cream\x1b[0m",
            ),
            (
                lambda: Tinta().mint("Mint").white("\nice cream\nis the")._("\nbest"),
                "\x1b[38;5;84mMint\x1b[38;5;255m\nice cream\nis the\x1b[38;5;255;4m\nbest\x1b[0m",
            ),
            (
                lambda: Tinta("\n").mint("Mint\n").white("ice cream is the")._("best"),
                "\n\x1b[38;5;84mMint\n\x1b[38;5;255mice cream is the \x1b[38;5;255;4mbest\x1b[0m",
            ),
        ],
    )
    def test_newlines_in_chaining(self, Testa: Callable[[], Tinta], expected: str):
        s = Testa().to_str()
        Testa().print()
        assert s == expected


class TestUnicode:

    def test_unicode(self):
        Tinta().pink("I ♡ Unicorns").print()
        assert (
            Tinta().pink("I ♡ Unicorns").to_str() == "\x1b[38;5;197mI ♡ Unicorns\x1b[0m"
        )

    def test_box_drawing(self):
        s = f"┌{'─'*14}┐\n│ I ♡ Unicorns │\n└{'─'*14}┘"
        Tinta("\n").mint(s).print()
        assert (
            Tinta().mint(s).to_str()
            == f"\x1b[38;5;84m┌──────────────┐\n│ I ♡ Unicorns │\n└──────────────┘\x1b[0m"
        )

    def test_emoji(self):
        Tinta("🦄").print()
        assert Tinta("🦄").to_str() == "🦄"

    def test_emoji_with_color(self):
        Tinta().purple("🦄").print()
        assert Tinta().purple("🦄").to_str() == "\x1b[38;5;18m🦄\x1b[0m"

    def test_emoji_with_color_and_clear(self):
        Tinta().pink("🦄").clear("🦄").print()
        assert (
            Tinta().pink("🦄").clear("🦄").to_str(sep="")
            == "\x1b[38;5;197m🦄\x1b[0m🦄\x1b[0m"
        )

    def test_emoji_with_color_and_clear_and_emoji(self):
        Tinta().purple("🦄").clear("🦄").pink("🦄").print()
        assert (
            Tinta().purple("🦄").clear("🦄").pink("🦄").to_str()
            == "\x1b[38;5;18m🦄 \x1b[0m🦄 \x1b[38;5;197m🦄\x1b[0m"
        )


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

    def test_missing_color(self):
        with pytest.raises(Exception):
            Tinta().sparkle().print()

    def test_color_same_as_builtin_method(self):
        with pytest.raises(Exception):
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


class TestMultipleInstances:

    def test_same_instance_chains_to_str(self):
        t = Tinta()
        red = "\x1b[38;5;1mRed"
        green = "\x1b[38;5;35mGreen"
        blue = "\x1b[38;5;32mBlue"
        assert t.red("Red").to_str() == f"{red}\x1b[0m"
        assert t.green("Green").to_str() == f"{red} {green}\x1b[0m"
        assert t.blue("Blue").to_str() == f"{red} {green} {blue}\x1b[0m"

    def test_same_instance_resets_after_print(self):
        t = Tinta()
        red = "\x1b[38;5;1mRed"
        green = "\x1b[38;5;35mGreen"
        blue = "\x1b[38;5;32mBlue"
        assert t.red("Red").to_str() == f"{red}\x1b[0m"
        t.print()
        assert t.green("Green").to_str() == f"{green}\x1b[0m"
        t.print()
        assert t.blue("Blue").to_str() == f"{blue}\x1b[0m"

    def test_multiple_instances_dont_interfere(self):
        t1 = Tinta()
        t2 = Tinta()
        t3 = Tinta()
        red = "\x1b[38;5;1mRed"
        green = "\x1b[38;5;35mGreen"
        blue = "\x1b[38;5;32mBlue"
        assert t1.red("Red").to_str() == f"{red}\x1b[0m"
        assert t2.green("Green").to_str() == f"{green}\x1b[0m"
        assert t3.blue("Blue").to_str() == f"{blue}\x1b[0m"


# @pytest.mark.skip
class TestFeatures:

    def test_inspect(self):
        assert Tinta().inspect(code=0) == "default"
        assert Tinta().inspect(name="default") == 0

        assert Tinta().inspect(code=35) == "green"
        assert Tinta().inspect(name="green") == 35

    @pytest.mark.parametrize(
        "Testa,expected",
        [
            (lambda: Tinta("Hello")("world"), "Hello world"),
            (lambda: Tinta("Hello ")("world"), "Hello  world"),
            (lambda: Tinta("Hello")(", world"), "Hello, world"),
            (lambda: Tinta("Hello,")("world"), "Hello, world"),
            (lambda: Tinta("Hello")(",")("world"), "Hello, world"),
            (lambda: Tinta("Hello world")("!"), "Hello world!"),
            (lambda: Tinta("Nice")("."), "Nice."),
            (lambda: Tinta("Nice")(".gif file"), "Nice .gif file"),
            (lambda: Tinta(" *** Important"), " *** Important"),
            (lambda: Tinta(", world"), ", world"),
            (lambda: Tinta(" , world"), " , world"),
            (lambda: Tinta(",")("world"), ", world"),
            (lambda: Tinta(" ,")("world"), " , world"),
            (lambda: Tinta(" ,")(" world"), " ,  world"),
            (
                lambda: Tinta()
                .red(" *** Important : Smart fix punctuation should work with")
                .green("ANSI")
                .red(", as well as plaintext."),
                "\x1b[38;5;1m *** Important : Smart fix punctuation should work with \x1b[38;5;35mANSI\x1b[38;5;1m, as well as plaintext.\x1b[0m",
            ),
        ],
    )
    def test_smart_fix_punctuation(self, Testa: Callable[[], Tinta], expected: str):
        assert Testa().to_str() == expected


class TestComplexStructure:

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
            Tinta(f"A {dog} is a human's best friend").to_str(plaintext=True)
            == "A cat is a human's best friend"
        )
        assert Tinta(f"A {Tinta().red('hologram').to_str()} is a human's best friend")

    def test_push(self):
        t = Tinta().push("How long").push("can two people talk about nothing?")
        assert t.to_str(plaintext=True) == "How long can two people talk about nothing?"

        assert len(t.parts) == 2
        assert len(t.parts_fmt) == 2
        assert len(t.parts_pln) == 2

        t = Tinta().push("How long", "can two people talk about nothing?")
        assert t.to_str(plaintext=True) == "How long can two people talk about nothing?"

        assert len(t.parts) == 1
        assert len(t.parts_fmt) == 1
        assert len(t.parts_pln) == 1

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
    def test_to_str(self, inputs: Tuple[str], expected):
        t = Tinta().push(*inputs)
        assert t.to_str(plaintext=True) == expected
        assert t.to_str(plaintext=True) == expected

    def test_pop(self):
        t = Tinta().push("How long").push("can two people talk about nothing?")
        t.pop()
        assert t.to_str(plaintext=True) == "How long"
        assert len(t.parts) == 1
        assert len(t.parts_fmt) == 1
        assert len(t.parts_pln) == 1

        t = Tinta()
        for p in range(10):
            t.push(str(p))

        assert len(t.parts) == 10
        t.pop(10)

        assert len(t.parts) == 0

        t.pop(2)  # Shouldn't error if we remove more than we have

        assert len(t.parts) == 0

    def test_zero_handles_clear(self):
        s = (
            Tinta("White")
            .red("Red")
            .green("Green")
            .blue("Blue")
            .tint(0, "Clear")
            .to_str(sep=" ")
        )
        print(s)
        assert (
            s
            == "White \x1b[38;5;1mRed \x1b[38;5;35mGreen \x1b[38;5;32mBlue \x1b[0mClear\x1b[0m"
        )


class TestUtils:

    @pytest.mark.parametrize(
        "test_str,expected",
        [
            (Tinta().blue("blue").to_str(), "blue"),
            (Tinta().red("red").to_str(), "red"),
            (Tinta().green("green").to_str(), "green"),
            (Tinta().yellow("yellow").to_str(), "yellow"),
            (Tinta().pink("🦄").to_str(), "🦄"),
            (
                Tinta()
                .pink("Pink unicorns 🦄")
                .purple("are as good as purple 🦄 ones")
                .to_str(),
                "Pink unicorns 🦄 are as good as purple 🦄 ones",
            ),
            (
                Tinta()
                .purple("Hello purple world!")
                .clear("I've got a song to sing about")
                ._("unicorns 🦄")
                .to_str(),
                "Hello purple world! I've got a song to sing about unicorns 🦄",
            ),
        ],
    )
    def test_strip_ansi(self, test_str: str, expected: str):
        assert Tinta.strip_ansi(test_str) == expected
