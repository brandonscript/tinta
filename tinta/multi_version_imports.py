#!/usr/bin/env python

# Tinta — Copyright (c) 2026 github.com/brandonscript
# Licensed under the MIT License. See LICENSE.

from typing import Callable, Literal, ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")
R = TypeVar("R")
GenericCallable = Callable[P, R]

__all__ = [
    "GenericCallable",
    "Literal",
    "T",
    "TypeVar",
]
