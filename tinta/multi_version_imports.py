import sys
from typing import Any, Callable

# Literal
if sys.version_info >= (3, 8):
    from typing import Literal
elif sys.version_info >= (3, 5):
    from typing_extensions import Literal
else:
    from typing import Literal

# TypeVar
if sys.version_info >= (3, 5):
    from typing import TypeVar

    T = TypeVar("T")

# ParamSpec, GenericCallable
if sys.version_info >= (3, 10):
    from typing import Literal, ParamSpec

    P = ParamSpec("P")
    R = TypeVar("R")  # type: ignore
    GenericCallable = Callable[P, R]
else:
    GenericCallable = Any

all = [
    GenericCallable,
    Literal,
    T,
    TypeVar,
]
