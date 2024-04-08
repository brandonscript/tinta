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
import time
import timeit
from contextlib import contextmanager
from typing import Any, Callable, Dict, List, Tuple

import pytest
from pytest import CaptureFixture

from tinta import Tinta

# pylint: disable=import-error
from tinta.stylize import _join, ansi_styles

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
BOLD, BOLD_OFF = ansi_styles("bold")
UNDERLINE, UNDERLINE_OFF = ansi_styles("underline")
DIM, DIM_OFF = ansi_styles("dim")
STRIKE, STRIKE_OFF = ansi_styles("strikethrough")


def _stitch(*args):
    # get everything after \x1b[ for each arg
    codes = [re.search(r"\x1b\[(.*?)m", arg).group(1) for arg in args]
    return f"\x1b[{_join(*codes).strip(';')}m"


@contextmanager
def skip_on_github_actions():
    gh = bool(os.getenv("GITHUB_ACTIONS") == "true")
    if gh:
        pytest.mark.skipif(True, reason="Function skipped on GitHub Actions")
    yield gh


class TestInit:

    def test_init(self):
        assert len(Tinta("initialized").parts) == 1

    def test_accepts_string_on_init(self):
        assert Tinta("initialized").to_str() == "initialized"


class TestBasicColorizing:

    basic_colors = [
        # fmt: off
        ("green", lambda: Tinta().green("green"), f"{GREEN}green{O}"),
        ("green", lambda: Tinta().tint(35, "green"), f"{GREEN}green{O}"),
        ("green", lambda: Tinta().tint("green", "green"), f"{GREEN}green{O}"),
        ("red", lambda: Tinta().red("red"), f"{RED}red{O}"),
        ("blue", lambda: Tinta().blue("blue"), f"{BLUE}blue{O}"),
        ("blue", lambda: Tinta().blue("green (but actually blue)"), f"{BLUE}green (but actually blue){O}"),
        ("light_blue", lambda: Tinta().light_blue("light_blue"), f"{L_BLUE}light_blue{O}"),
        ("yellow", lambda: Tinta().yellow("yellow"), f"{YELLOW}yellow{O}"),
        ("amber", lambda: Tinta().amber("amber"), f"{AMBER}amber{O}"),
        ("mint", lambda: Tinta().mint("mint"), f"{MINT}mint{O}"),
        ("olive", lambda: Tinta().olive("olive"), f"{OLIVE}olive{O}"),
        ("orange", lambda: Tinta().orange("orange"), f"{ORANGE}orange{O}"),
        ("purple", lambda: Tinta().purple("purple"), f"{PURPLE}purple{O}"),
        ("pink", lambda: Tinta().pink("pink"), f"{PINK}pink{O}"),
        ("gray", lambda: Tinta().gray("gray"), f"{GRAY}gray{O}"),
        ("dark_gray", lambda: Tinta().dark_gray("dark_gray"), f"{D_GRAY}dark_gray{O}"),
        ("light_gray", lambda: Tinta().light_gray("light_gray"), f"{L_GRAY}light_gray{O}"),
        ("white", lambda: Tinta().white("white"), f"{WHITE}white{O}"),
        # fmt: on
    ]

    @pytest.mark.parametrize(
        "color,Testa,expected",
        basic_colors,
    )
    def test_print_colors(self, color, Testa, expected, perf):
        Testa().print()

    @pytest.mark.parametrize(
        "color,Testa,expected",
        basic_colors,
    )
    def test_check_output(self, color, Testa, expected, perf):
        assert Testa().to_str() == expected

    def test_sandwich_colors(self):
        assert (
            Tinta("plain").green("green").default("plain").to_str()
            == f"plain {GREEN}green{O} plain"
        )

    def test_clear_resets_color(self):
        Tinta().green("green").clear("plain").print()
        assert (
            Tinta().green("green").clear("plain")("string").to_str()
            == f"{GREEN}green{O} plain string"
        )


class TestBasicStylizing:

    def test_bold(self):
        b = Tinta().bold("bold")
        assert b.to_str() == f"{BOLD}bold{O}"
        b.print()

        b = Tinta().b("bold")
        assert b.to_str() == f"{BOLD}bold{O}"
        b.print()

    def test_normal_resets_bold(self):
        b = Tinta().bold("bold").normal("normal")
        assert b.to_str() == f"{BOLD}bold{O} normal"
        b.print()

    def test_bold_resets_bold(self):
        b = Tinta("To").bold().red("boldly").bold().white("go")
        assert b.to_str() == f"To {_stitch(BOLD, RED)}boldly{O} {WHITE}go{O}"
        b.print()

    def test_bold_resets_only_bold(self):
        b = Tinta("To").bold().underline().red("boldly").bold().white("go")
        assert (
            b.to_str()
            == f"To {_stitch(BOLD, UNDERLINE, RED)}boldly{BOLD_OFF} {WHITE}go{O}"
        )
        b.print()

    def test_underline(self):
        u = Tinta().underline("underline")
        assert u.to_str() == f"{UNDERLINE}underline{O}"
        u.print()

        _ = Tinta()._("underscore")
        assert _.to_str() == f"{UNDERLINE}underscore{O}"
        _.print()

    def test_normal_resets_underline(self):
        u = Tinta().underline("underline").normal("normal")
        assert u.to_str() == f"{UNDERLINE}underline{O} normal"
        u.print()

    def test_underline_resets_underline(self):
        u = Tinta("To")._().amber("underlinely")._().purple("go")
        assert (
            u.to_str() == f"To {_stitch(UNDERLINE, AMBER)}underlinely{O} {PURPLE}go{O}"
        )
        u.print()

    def test_underline_resets_only_underline(self):
        u = Tinta("To").underline().bold().amber("underlinely").underline().olive("go")
        assert (
            u.to_str()
            == f"To {_stitch(BOLD, UNDERLINE, AMBER)}underlinely{UNDERLINE_OFF} {OLIVE}go{O}"
        )
        u.print()

    def test_dim(self):
        d = Tinta().dim("dim")
        assert d.to_str() == f"{DIM}dim{O}"
        d.print()

    def test_normal_resets_dim(self):
        t = Tinta().dim("dim").normal("normal")
        assert t.to_str() == f"{DIM}dim{O} normal"
        t.print()

    def test_dim_resets_dim(self):
        d = Tinta("To").dim().olive("dimly").dim().blue("go")
        assert d.to_str() == f"To {_stitch(DIM, OLIVE)}dimly{O} {BLUE}go{O}"
        d.print()

    def test_dim_resets_only_dim(self):
        d = Tinta("To").dim().underline().olive("dimly").dim().blue("go")
        assert (
            d.to_str()
            == f"To {_stitch(DIM, UNDERLINE, OLIVE)}dimly{DIM_OFF} {BLUE}go{O}"
        )
        d.print()

    def test_strikethrough(self):
        s = Tinta().strikethrough("strikethrough")
        assert s.to_str() == f"{STRIKE}strikethrough{O}"
        s.print()

    def test_normal_resets_strikethrough(self):
        s = Tinta().strikethrough("strikethrough").normal("normal")
        assert s.to_str() == f"{STRIKE}strikethrough{O} normal"
        s.print()

    def test_strikethrough_resets_strikethrough(self):
        s = (
            Tinta("To")
            .strikethrough()
            .olive("strikethroughly")
            .strikethrough()
            .blue("go")
        )
        assert (
            s.to_str() == f"To {_stitch(STRIKE, OLIVE)}strikethroughly{O} {BLUE}go{O}"
        )
        s.print()

    def test_strikethrough_resets_only_strikethrough(self):
        s = (
            Tinta("To")
            .strikethrough()
            .underline()
            .olive("strikethroughly")
            .strikethrough()
            .blue("go")
        )
        assert (
            s.to_str()
            == f"To {_stitch(UNDERLINE, STRIKE, OLIVE)}strikethroughly{STRIKE_OFF} {BLUE}go{O}"
        )
        s.print()

    def test_bold_underline(self):
        bu = Tinta().bold("bold").underline("underline")
        assert bu.to_str() == f"{BOLD}bold {UNDERLINE}underline{O}"
        bu.print()

    def test_bold_dim(self):
        bd = Tinta().bold("bold").dim("dim")
        assert bd.to_str() == f"{BOLD}bold {DIM}dim{O}"
        bd.print()

    def test_underline_dim(self):
        ud = Tinta().underline("underline").dim("dim")
        assert ud.to_str() == f"{UNDERLINE}underline {DIM}dim{O}"
        ud.print()

    def test_bold_underline_dim(self):
        bud = Tinta().bold("bold").underline("underline").dim("dim")
        assert bud.to_str() == f"{BOLD}bold {UNDERLINE}underline {DIM}dim{O}"
        bud.print()

    def test_underline_bold_dim(self):
        ubd = Tinta().underline("underline").bold("bold").dim("dim")
        assert ubd.to_str() == f"{UNDERLINE}underline {BOLD}bold {DIM}dim{O}"
        ubd.print()

    def test_bold_strikethrough(self):
        bs = Tinta().bold("bold").strikethrough("strikethrough")
        assert bs.to_str() == f"{BOLD}bold {STRIKE}strikethrough{O}"
        bs.print()

    def test_underline_strikethrough(self):
        us = Tinta().underline("underline").strikethrough("strikethrough")
        assert us.to_str() == f"{UNDERLINE}underline {STRIKE}strikethrough{O}"
        us.print()

    def test_bold_underline_strikethrough(self):
        bus = Tinta().bold("bold").underline("underline").strikethrough("strikethrough")
        assert (
            bus.to_str() == f"{BOLD}bold {UNDERLINE}underline {STRIKE}strikethrough{O}"
        )
        bus.print()

    def test_styles_remain_until_normal(self):
        assert (
            Tinta()
            .bold("bold")
            .underline("underline")
            .dim("dim")
            .pink("pink")
            .normal()
            .pink("pink")
            .to_str()
            == f"{BOLD}bold {UNDERLINE}underline {DIM}dim {PINK}pink{_stitch(BOLD_OFF, UNDERLINE_OFF)} pink{O}"
        )


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
                f"{MINT}Mint{WHITE}\nice cream\nis the{UNDERLINE}\nbest{O}",
            ),
            (
                lambda: Tinta("\n").mint("Mint\n").white("ice cream is the")._("best"),
                f"\n{MINT}Mint\n{WHITE}ice cream is the {UNDERLINE}best{O}",
            ),
        ],
    )
    def test_newlines_in_chaining(self, Testa: Callable[[], Tinta], expected: str):
        s = Testa().to_str()
        Testa().print()
        assert s == expected

    def test_chaining_same_styles_doesnt_dupe(self):
        t = Tinta().green("green").green("green").green("green")
        assert t.to_str() == f"{GREEN}green green green{O}"
        t.print()


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
        t = Tinta().purple("🦄")
        assert Tinta().purple("🦄").to_str() == f"{PURPLE}🦄{O}"
        t.print()

    def test_emoji_with_color_and_clear(self):
        t = Tinta().pink("🦄").clear("🦄")
        assert t.to_str(sep="") == f"{PINK}🦄{O}🦄"
        t.print(sep="")

    def test_emoji_with_color_style_and_normal(self):
        t = Tinta().purple()._("🦄").normal("🦄").pink("🦄")
        assert (
            t.to_str()
            == f"{_stitch(UNDERLINE, PURPLE)}🦄{UNDERLINE_OFF} 🦄 {PINK}🦄{O}"
        )
        t.print()

    def test_emoji_with_color_style_and_clear(self):
        t = Tinta().purple()._("🦄").clear("🦄").pink("🦄")
        assert t.to_str() == f"{_stitch(UNDERLINE, PURPLE)}🦄{O} 🦄 {PINK}🦄{O}"
        t.print()


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

        Tinta._initialized = False
        Tinta._colors._initialized = False

        basic()

    def test_complete_example(self):
        from examples.complete_example import complete

        Tinta._initialized = False
        Tinta._colors._initialized = False

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

    def test_pop_updates_current_style(self):
        t = Tinta().green("green").red("red").blue("blue")
        t.pop()
        assert t.to_str(plaintext=True) == "green red"
        t.pop()
        assert t.to_str(plaintext=True) == "green"
        t.pop()
        assert t.to_str(plaintext=True) == ""

        t = Tinta().green("green").red("red").blue("blue").bold("bold n' blue")
        t.pop(2)
        assert t._styler == Tinta.Styler(color=RED)

    def test_tint_handles_zero(self):
        s = (
            Tinta("white")
            .red("red")
            .green("green")
            .blue("blue")
            .tint(0, "default")
            .to_str(sep=" ")
        )
        print(s)
        assert s == f"white {RED}red {GREEN}green {BLUE}blue{O} default"


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


class TestTiming:

    def test_basic_time_against_raw(self):
        base_start = time.perf_counter()
        print(
            f"{BLUE}blue {GREEN}green {L_BLUE}light blue {YELLOW}yellow {AMBER}amber {MINT}mint {OLIVE}olive {ORANGE}orange {PURPLE}purple {PINK}pink {GRAY}gray {D_GRAY}dark gray {L_GRAY}light gray {WHITE}white{O}"
        )
        base_end = time.perf_counter()

        tinta_start = time.perf_counter()

        (
            Tinta()
            .blue("blue")
            .green("green")
            .light_blue("light blue")
            .yellow("yellow")
            .amber("amber")
            .mint("mint")
            .olive("olive")
            .orange("orange")
            .purple("purple")
            .pink("pink")
            .gray("gray")
            .dark_gray("dark gray")
            .light_gray("light gray")
            .white("white")
            .print()
        )
        tinta_end = time.perf_counter()

        raw_diff = base_end - base_start
        tinta_diff = tinta_end - tinta_start

        print(f"Raw: {raw_diff:.4f} seconds")
        print(f"Tinta: {tinta_diff:.4f} seconds")

        assert tinta_diff - raw_diff < 0.001

    def test_with_timeit(self):

        count = 500

        tinta_time = timeit.timeit(
            lambda: Tinta()
            .blue("blue")
            .green("green")
            .light_blue("light blue")
            .yellow("yellow")
            .amber("amber")
            .mint("mint")
            .olive("olive")
            .orange("orange")
            .purple("purple")
            .pink("pink")
            .gray("gray")
            .dark_gray("dark gray")
            .light_gray("light gray")
            .white("white")
            .print(),
            number=count,
        )

        class FakeClass:
            def __init__(self):
                self.blue = "blue"
                self.green = "green"
                self.light_blue = "light blue"
                self.yellow = "yellow"
                self.amber = "amber"
                self.mint = "mint"
                self.olive = "olive"
                self.orange = "orange"
                self.purple = "purple"
                self.pink = "pink"
                self.gray = "gray"
                self.dark_gray = "dark gray"
                self.light_gray = "light gray"
                self.white = "white"

            def print(self):
                print(
                    f"{BLUE}{self.blue} {GREEN}{self.green} {L_BLUE}{self.light_blue} {YELLOW}{self.yellow} {AMBER}{self.amber} {MINT}{self.mint} {OLIVE}{self.olive} {ORANGE}{self.orange} {PURPLE}{self.purple} {PINK}{self.pink} {GRAY}{self.gray} {D_GRAY}{self.dark_gray} {L_GRAY}{self.light_gray} {WHITE}{self.white}{O}"
                )

        class_time = timeit.timeit(
            lambda: FakeClass().print(),
            number=count,
        )

        raw_time = timeit.timeit(
            lambda: print(
                f"{BLUE}blue {GREEN}green {L_BLUE}light blue {YELLOW}yellow {AMBER}amber {MINT}mint {OLIVE}olive {ORANGE}orange {PURPLE}purple {PINK}pink {GRAY}gray {D_GRAY}dark gray {L_GRAY}light gray {WHITE}white{O}"
            ),
            number=count,
        )

        print(f"Raw: {raw_time:.4f} seconds")
        print(f"Class: {class_time:.4f} seconds")
        print(f"Tinta: {tinta_time:.4f} seconds")

        assert tinta_time - raw_time < 0.5
