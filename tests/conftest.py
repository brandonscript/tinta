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

import pytest

if os.getenv("_PYTEST_RAISE", "0") != "0":

    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(call):
        raise call.excinfo.value

    @pytest.hookimpl(tryfirst=True)
    def pytest_internalerror(excinfo):
        raise excinfo.value


def pytest_addoption(parser):
    parser.addoption("--perf", action="store_true", help="measure performance of tests")


@pytest.fixture(scope="session")
def perf(request):
    import tinta.constants as C

    if request.config.option.perf is True:
        C.PERF_MEASURE = True


@pytest.fixture(scope="function", autouse=False)
def alt_colors_ini(tmp_path):

    from tinta import Tinta

    colors_ini = tmp_path / "colors.ini"
    colors_ini.write_text(
        """[colors]
sparkle = 195
dragons_breath = 202
"""
    )

    orig_colors_ini = Tinta._colors._colors_ini_path

    Tinta.load_colors(colors_ini)
    yield colors_ini
    Tinta.load_colors(orig_colors_ini)


@pytest.fixture(scope="function", autouse=False)
def clobber_colors_ini(tmp_path):

    from tinta import Tinta

    colors_ini = tmp_path / "colors.ini"
    colors_ini.write_text(
        """[colors]
default: 256
grey: 242
dark_grey: 237
light_grey: 250
mint: 43
green: 78
blue: 33
purple: 99
amber: 214
amber_accent: 222
orange: 208
orange_accent: 214
red: 161
red_accent: 175
pink: 205
light_pink: 211
dark_pink: 89
"""
    )

    orig_colors_ini = Tinta._colors._colors_ini_path

    Tinta.load_colors(colors_ini)
    yield colors_ini
    Tinta.load_colors(orig_colors_ini)
