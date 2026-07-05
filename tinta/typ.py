#!/usr/bin/env python

# Tinta — Copyright (c) 2026 github.com/brandonscript
# Licensed under the MIT License. See LICENSE.

"""This module contains type hints and utility functions for Tinta."""
import functools
from typing import Any, Callable, cast

from .multi_version_imports import GenericCallable, Literal

StringType = Literal["pln", "esc", "fmt"]  # type: ignore


class MissingColorError(Exception):
    """Raised when a color is not found in the colors.ini file."""

    ...


class InvalidStyleError(Exception):
    """Raised when an invalid style is passed to a function."""

    ...


class InvalidColorError(Exception):
    """Raised when an invalid color is passed to a function."""

    ...


def copy_kwargs(func: GenericCallable) -> Callable[..., GenericCallable]:
    """Decorator does nothing but casts the original function to match the given function signature"""

    @functools.wraps(func, updated=())
    def _cast_func(_func: Callable[..., Any]) -> GenericCallable:
        return cast(GenericCallable, _func)

    if not callable(func):
        raise RuntimeError(
            f"You must pass a function to this decorator, got {func} instead."
        )

    return _cast_func


def parse_bool(value: Any) -> bool:
    """Parses a string value to a boolean value."""
    if isinstance(value, bool):
        return value
    return str(value).lower() in ("true", "1", "t", "y", "yes")
