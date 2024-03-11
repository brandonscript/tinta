#!/usr/bin/env python

# Tinta
# Copyright 2024 github.com/brandoncript

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# If you use this software, you must also agree under the terms of the Hippocratic License 3.0 to not use this software in a way that directly or indirectly causes harm. You can find the full text of the license at https://firstdonoharm.dev.

"""This module contains type hints and utility functions for Tinta."""
import functools
import inspect
import sys
from typing import Any, Callable, cast

if sys.version_info >= (3, 10):
    from typing import Literal, ParamSpec, TypeVar

    P = ParamSpec("P") if sys.version_info >= (3, 10) else ...  # type: ignore
    R = TypeVar("R")  # type: ignore

    GenericCallable = Callable[P, R]
elif sys.version_info >= (3, 8):
    from typing import Literal

    GenericCallable = Any
else:
    from typing_extensions import Literal

    GenericCallable = Any


StringType = Literal["pln", "esc", "fmt"]  # type: ignore


class MissingColorError(Exception):
    """Raised when a color is not found in the colors.ini file."""

    pass


def copy_kwargs(func: GenericCallable) -> Callable[..., GenericCallable]:
    """Decorator does nothing but casts the original function to match the given function signature"""

    @functools.wraps(func, updated=())
    def _cast_func(_func: Callable[..., Any]) -> GenericCallable:
        return cast(GenericCallable, _func)

    if inspect.isfunction(func):
        return _cast_func

    raise RuntimeError("You must pass a function to this decorator.")


def parse_bool(value: Any) -> bool:
    """Parses a string value to a boolean value."""
    if isinstance(value, bool):
        return value
    return str(value).lower() in ("true", "1", "t", "y", "yes")
