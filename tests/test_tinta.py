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


import os
import re
from contextlib import contextmanager
from typing import Any, Callable, Dict, List, Tuple

import pytest
from pytest import CaptureFixture

# pylint: disable=import-error
from tinta import Tinta

Tinta.load_colors("examples/colors.ini")

O = "\x1b[0m"
GREEN = "\x1b[38;5;35m"
RED = "\x1b[38;5;1m"
BLUE = "\x1b[38;5;32m"
L_BLUE = "\x1b[38;5;37m"
YELLOW = "\x1b[38;5;214m"
AMBER = "\x1b[38;5;208m"
MINT = "\x1b[38;5;43m"
OLIVE = "\x1b[38;5;106m"
ORANGE = "\x1b[38;5;166m"
PURPLE = "\x1b[38;5;18m"
PINK = "\x1b[38;5;197m"
GRAY = "\x1b[38;5;243m"
D_GRAY = "\x1b[38;5;235m"
L_GRAY = "\x1b[38;5;248m"
WHITE = "\x1b[38;5;255m"


@contextmanager
def skip_on_github_actions():
    gh = bool(os.getenv("GITHUB_ACTIONS") == "true")
    if gh:
        pytest.mark.skipif(True, reason="Function skipped on GitHub Actions")
    yield gh


class TestInit:

    def test_init(self):
        assert len(Tinta("initialized").parts) == 1


class TestBasicColorizing:

    @pytest.mark.parametrize(
        "color,Testa,expected",
        [
            # fmt: off
            ("green", lambda: Tinta().green("green"), f"{GREEN}green{O}"),
            ("green", lambda: Tinta().tint(35, "green"), f"{GREEN}green{O}"),
            ("green", lambda: Tinta().tint("green", "green"), f"{GREEN}green{O}"),
            ("red", lambda: Tinta().red("red"), f"{RED}red{O}"),
            ("blue", lambda: Tinta().blue("blue"), f"{BLUE}blue{O}"),
            ("blue", lambda: Tinta().blue("Green"), f"{BLUE}Green{O}"),
            ("light_blue", lambda: Tinta().light_blue("light_blue"), f"{L_BLUE}light_blue{O}"),
            ("yellow", lambda: Tinta().yellow("yellow"), f"{YELLOW}yellow{O}"),
            ("amber", lambda: Tinta().amber("amber"), f"{AMBER}amber{O}"),
            ("mint", lambda: Tinta().mint("Mint"), f"{MINT}Mint{O}"),
            ("olive", lambda: Tinta().olive("olive"), f"{OLIVE}olive{O}"),
            ("orange", lambda: Tinta().orange("orange"), f"{ORANGE}orange{O}"),
            ("purple", lambda: Tinta().purple("purple"), f"{PURPLE}purple{O}"),
            ("pink", lambda: Tinta().pink("pink"), f"{PINK}pink{O}"),
            ("gray", lambda: Tinta().gray("gray"), f"{GRAY}gray{O}"),
            ("dark_gray", lambda: Tinta().dark_gray("dark_gray"), f"{D_GRAY}dark_gray{O}"),
            ("light_gray", lambda: Tinta().light_gray("light_gray"), f"{L_GRAY}light_gray{O}"),
            ("white", lambda: Tinta().white("white"), f"{WHITE}white{O}"),
            # fmt: on
        ],
    )
    def test_colors(self, color, Testa, expected):
        Testa().print()
        assert Testa().to_str() == expected


class TestChaining:

    @pytest.mark.parametrize(
        "Testa, kwargs, expected",
        [
            # fmt: off
            (lambda: Tinta().green("green").red("red").blue("blue"), {"sep":"", "plaintext":True}, "greenredblue"),
            (lambda: Tinta().green("green").red("red").blue("blue"), {"plaintext": True}, "green red blue"),
            (lambda: Tinta().green("green").red("red").blue("blue"), {"sep": ""}, f"{GREEN}green{RED}red{BLUE}blue{O}"),
            (lambda: Tinta().green("green").red("red").blue("blue"), {}, f"{GREEN}green {RED}red {BLUE}blue{O}"),
            (lambda: Tinta().green("green").red("red").blue("blue "), {}, f"{GREEN}green {RED}red {BLUE}blue{O} "),
            (lambda: Tinta().green("green").red("red").blue("blue \n"), {}, f"{GREEN}green {RED}red {BLUE}blue{O} \n"),
            (lambda: Tinta().green("green").red("red").blue("blue").clear(), {}, f"{GREEN}green {RED}red {BLUE}blue{O}"),
            # fmt: on
        ],
    )
    def test_chaining_resets_correctly(
        self,
        Testa: Callable,
        kwargs: Dict[str, Any],
        expected: str,
        capfd: CaptureFixture[str],
    ):
        s = Testa().to_str(**kwargs)
        Testa().print(**kwargs)
        assert s == expected
        with skip_on_github_actions() as skip:
            if not skip:
                out = capfd.readouterr().out
                assert out == f"{expected}\n"

    @pytest.mark.parametrize(
        "Testa,expected",
        [
            (
                lambda: Tinta().mint("Mint\nice cream"),
                f"{MINT}Mint\nice cream{O}",
            ),
            (
                lambda: Tinta().mint("Mint").white("\nice cream\nis the")._("\nbest"),
                f"{MINT}Mint{WHITE}\nice cream\nis the\x1b[38;5;255;4m\nbest{O}",
            ),
            (
                lambda: Tinta("\n").mint("Mint\n").white("ice cream is the")._("best"),
                f"\n{MINT}Mint\n{WHITE}ice cream is the \x1b[38;5;255;4mbest{O}",
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
        assert Tinta().pink("I ♡ Unicorns").to_str() == f"{PINK}I ♡ Unicorns{O}"

    def test_box_drawing(self):
        s = f"┌{'─'*14}┐\n│ I ♡ Unicorns │\n└{'─'*14}┘"
        Tinta("\n").mint(s).print()
        assert (
            Tinta().mint(s).to_str()
            == f"{MINT}┌──────────────┐\n│ I ♡ Unicorns │\n└──────────────┘{O}"
        )

    def test_emoji(self):
        Tinta("🦄").print()
        assert Tinta("🦄").to_str() == "🦄"

    def test_emoji_with_color(self):
        Tinta().purple("🦄").print()
        assert Tinta().purple("🦄").to_str() == f"{PURPLE}🦄{O}"

    def test_emoji_with_color_and_clear(self):
        Tinta().pink("🦄").clear("🦄").print()
        assert Tinta().pink("🦄").clear("🦄").to_str(sep="") == f"{PINK}🦄\x1b[0m🦄{O}"

    def test_emoji_with_color_and_clear_and_emoji(self):
        Tinta().purple("🦄").clear("🦄").pink("🦄").print()
        assert (
            Tinta().purple("🦄").clear("🦄").pink("🦄").to_str()
            == f"{PURPLE}🦄 \x1b[0m🦄 {PINK}🦄{O}"
        )


class TestLowerLevel:

    ITS_NOT_EASY = "it's not easy being green"

    def assert_its_not_easy_being_green(self, out: str):
        assert self.ITS_NOT_EASY in out
        assert f"{GREEN}" in out

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

    def test_print_none(self):
        Tinta(None).print()

    def test_empty_color_call(self):
        t = Tinta("Plain").green()
        t.push("Green")
        t.print()

    def test_tint_color_0(self):
        Tinta().tint(0, "Zero").print()


class TestExamples:

    def test_basic_example(self):
        from examples.basic_example import basic

        basic()

    def test_complete_example(self):
        from examples.complete_example import complete

        complete()


class TestWhiteSpace:

    def test_print_whitespace(self):
        Tinta(" ").print()

    whitespace_cases = [
        (lambda: Tinta("Hello\nWorld"), "Hello\nWorld"),
        (lambda: Tinta("\nHello\nWorld"), "\nHello\nWorld"),
        (lambda: Tinta("\nHello\nWorld\n"), "\nHello\nWorld\n"),
        (lambda: Tinta("\nHello\nWorld\n\n"), "\nHello\nWorld\n\n"),
        (lambda: Tinta("Hello\nWorld\n"), "Hello\nWorld\n"),
        (lambda: Tinta("Hello World\n"), "Hello World\n"),
        (lambda: Tinta("Hello World"), "Hello World"),
        (lambda: Tinta("Hello World "), "Hello World "),
        (lambda: Tinta(" Hello World "), " Hello World "),
        (lambda: Tinta(" Hello World"), " Hello World"),
        (lambda: Tinta("  Hello World"), "  Hello World"),
        (lambda: Tinta("  Hello World "), "  Hello World "),
        (lambda: Tinta("  Hello World  "), "  Hello World  "),
        (lambda: Tinta(" Hello World\n"), " Hello World\n"),
        (lambda: Tinta(" Hello World\n "), " Hello World\n "),
        (lambda: Tinta(" Hello World\n  "), " Hello World\n  "),
        (lambda: Tinta(" Hello World\n\n"), " Hello World\n\n"),
        (lambda: Tinta(" Hello World\n\n "), " Hello World\n\n "),
        (lambda: Tinta("\nHello World \n"), "\nHello World \n"),
        (lambda: Tinta("\nHello World \n "), "\nHello World \n "),
        (lambda: Tinta("\n Hello World \n\n"), "\n Hello World \n\n"),
        (lambda: Tinta("\n Hello\n World \n"), "\n Hello\n World \n"),
    ]

    @pytest.mark.parametrize(
        "Testa,expected",
        whitespace_cases,
    )
    def test_uncolored_respects_whitespace(
        self, Testa: Callable[[], Tinta], expected: str, capfd: CaptureFixture[str]
    ):
        s = Testa().to_str()
        assert s == expected
        Testa().print()
        with skip_on_github_actions() as skip:
            if not skip:
                out = capfd.readouterr().out
                assert out == f"{expected}\n"

    @pytest.mark.parametrize(
        "Testa,expected",
        whitespace_cases,
    )
    def test_uncolored_plaintext_respects_whitespace(
        self, Testa: Callable[[], Tinta], expected: str, capfd: CaptureFixture[str]
    ):
        p = Testa().to_str(plaintext=True)
        assert p == expected
        Testa().print(plaintext=True)
        with skip_on_github_actions() as skip:
            if not skip:
                out = capfd.readouterr().out
                assert out == f"{expected}\n"

    @pytest.mark.parametrize(
        "Testa,expected",
        whitespace_cases,
    )
    def test_proxy_color_to_str_respects_whitespace(
        self, Testa: Callable[[], Tinta], expected: str, capfd: CaptureFixture[str]
    ):
        s = Testa().to_str()
        found = re.search(r"\s+$", expected)
        trail_ws = found.group() if found else ""
        _expected = f"{PURPLE}{expected.rstrip()}{O}{trail_ws}"
        #                                         ^^^^^^^^^^^^^
        # Reset ANSI char is always placed before trailing whitespace
        assert Tinta().purple(s).to_str() == _expected
        Tinta().purple(s).print()
        with skip_on_github_actions() as skip:
            if not skip:
                out = capfd.readouterr().out
                assert out == f"{_expected}\n"

    @pytest.mark.parametrize(
        "Testa,expected",
        whitespace_cases,
    )
    def test_proxy_color_to_plaintext_respects_whitespace(
        self, Testa: Callable[[], Tinta], expected: str, capfd: CaptureFixture[str]
    ):
        p = Testa().to_str(plaintext=True)
        assert Tinta().purple(p).to_str(plaintext=True) == expected
        Tinta().purple(p).print(plaintext=True)
        with skip_on_github_actions() as skip:
            if not skip:
                out = capfd.readouterr().out
                assert out == f"{expected}\n"

    @pytest.mark.parametrize(
        "Testa,expected",
        whitespace_cases,
    )
    def test_proxy_color_chain_to_str_respects_whitespace(
        self, Testa: Callable[[], Tinta], expected: str, capfd: CaptureFixture[str]
    ):
        s = Testa().to_str()
        found = re.search(r"\s+$", expected)
        trail_ws = found.group() if found else ""
        expected_purple = f"{PURPLE}{expected}"
        expected_pink = f"{PINK}{expected.rstrip()}{O}{trail_ws}"
        l_or_r_newline = expected.startswith("\n") or expected.endswith("\n")
        sep = "" if l_or_r_newline else " "
        # ^ If there is a newline at the end of the current or start of the next segment,
        #   Tinta will ignore the separator
        assert (
            Tinta().purple(s).pink(s).to_str()
            == f"{expected_purple}{sep}{expected_pink}"
        )
        Tinta().purple(s).pink(s).print()
        with skip_on_github_actions() as skip:
            if not skip:
                out = capfd.readouterr().out
                assert out == f"{expected_purple}{sep}{expected_pink}\n"

    @pytest.mark.parametrize(
        "Testa,expected",
        whitespace_cases,
    )
    def test_proxy_color_chain_to_plaintext_respects_whitespace(
        self, Testa: Callable[[], Tinta], expected: str, capfd: CaptureFixture[str]
    ):
        p = Testa().to_str(plaintext=True)
        l_or_r_newline = expected.startswith("\n") or expected.endswith("\n")
        sep = "" if l_or_r_newline else " "
        # ^ If there is a newline at the end of the current or start of the next segment,
        #   Tinta will ignore the separator
        assert (
            Tinta().purple(p).pink(p).to_str(plaintext=True)
            == f"{expected}{sep}{expected}"
        )
        Tinta().purple(p).pink(p).print(plaintext=True)
        with skip_on_github_actions() as skip:
            if not skip:
                out = capfd.readouterr().out
                assert out == f"{expected}{sep}{expected}\n"

    def test_sep_inherits_prev_part_color(self):
        assert (
            Tinta().red("Red").green("Green").blue("Blue").to_str(sep=";")
            == f"{RED}Red;{GREEN}Green;{BLUE}Blue{O}"
        )


class TestMultipleInstances:

    def test_same_instance_chains_to_str(self):
        t = Tinta()
        red = f"{RED}Red"
        green = f"{GREEN}Green"
        blue = f"{BLUE}Blue"
        assert t.red("Red").to_str() == f"{red}{O}"
        assert t.green("Green").to_str() == f"{red} {green}{O}"
        assert t.blue("Blue").to_str() == f"{red} {green} {blue}{O}"

    def test_same_instance_resets_after_print(self):
        t = Tinta()
        assert t.red("Red").to_str() == f"{RED}Red{O}"
        t.print()
        assert t.green("Green").to_str() == f"{GREEN}Green{O}"
        t.print()
        assert t.blue("Blue").to_str() == f"{BLUE}Blue{O}"

    def test_multiple_instances_dont_interfere(self):
        t1 = Tinta()
        t2 = Tinta()
        t3 = Tinta()
        assert t1.red("Red").to_str() == f"{RED}Red{O}"
        assert t2.green("Green").to_str() == f"{GREEN}Green{O}"
        assert t3.blue("Blue").to_str() == f"{BLUE}Blue{O}"


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
                f"{RED} *** Important : Smart fix punctuation should work with {GREEN}ANSI{RED}, as well as plaintext.{O}",
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
        assert s == f"White {RED}Red {GREEN}Green {BLUE}Blue {O}Clear{O}"


class TestUtils:

    @pytest.mark.parametrize(
        "Testa,expected",
        [
            # fmt: off
            (lambda: Tinta().blue("blue"), "blue"),
            (lambda: Tinta().red("red"), "red"),
            (lambda: Tinta().green("green"), "green"),
            (lambda: Tinta().yellow("yellow"), "yellow"),
            (lambda: Tinta().pink("🦄"), "🦄"),
            # fmt: on
            (
                lambda: Tinta()
                .pink("Pink unicorns 🦄")
                .purple("are as good as purple 🦄 ones"),
                "Pink unicorns 🦄 are as good as purple 🦄 ones",
            ),
            (
                lambda: Tinta()
                .purple("Hello purple world!")
                .clear("I've got a song to sing about")
                ._("unicorns 🦄"),
                "Hello purple world! I've got a song to sing about unicorns 🦄",
            ),
        ],
    )
    def test_strip_ansi(self, Testa: Callable, expected: str):
        assert Tinta.strip_ansi(Testa().to_str()) == expected

    @pytest.mark.parametrize(
        "Testa, ljust, fillchar, expected",
        [
            # fmt: off
            (lambda: Tinta().mint("🦄"), 10, " ", f"{MINT}🦄{O}         "),
            (lambda: Tinta().mint("I love unicorns and magical fruit"), 10, " ", f"{MINT}I love unicorns and magical fruit{O}"),
            (lambda: Tinta("ljust"), 13, "-", f"ljust{'-'*8}"),
            # fmt: on
            (
                lambda: Tinta("Wild")
                .purple("unicorns")
                .pink("like their")
                .mint("space"),
                20,
                " ",
                f"Wild {PURPLE}unicorns {PINK}like their {MINT}space{O}",
            ),
            (
                lambda: Tinta("a").purple("b").pink("c d").mint("e "),
                80,
                " ",
                f"a {PURPLE}b {PINK}c d {MINT}e{O} {' '*70}",
            ),
        ],
    )
    def test_ljust(self, Testa: Callable, ljust: int, fillchar: str, expected: str):
        assert Tinta.ljust(Testa().to_str(), ljust, fillchar) == expected

    @pytest.mark.parametrize(
        "Testa, rjust, fillchar, expected",
        [
            # fmt: off
            (lambda: Tinta().mint("🦄"), 10, " ", f"         {MINT}🦄{O}"),
            (lambda: Tinta().mint("I love unicorns and magical fruit"), 10, " ", f"{MINT}I love unicorns and magical fruit{O}"),
            (lambda: Tinta("rjust"), 13, "-", f"{'-'*8}rjust"),
            # fmt: on
            (
                lambda: Tinta("Wild")
                .purple("unicorns")
                .pink("like their")
                .mint("space"),
                20,
                " ",
                f"Wild {PURPLE}unicorns {PINK}like their {MINT}space{O}",
            ),
            (
                lambda: Tinta(" a").purple("b").pink("c d").mint("e"),
                80,
                " ",
                f"{' '*70} a {PURPLE}b {PINK}c d {MINT}e{O}",
            ),
        ],
    )
    def test_rjust(self, Testa: Callable, rjust: int, fillchar: str, expected: str):
        assert Tinta.rjust(Testa().to_str(), rjust, fillchar) == expected
