import functools
import inspect
from collections.abc import Callable
from typing import Any, cast

from typing_extensions import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def copy_kwargs(func: Callable[P, R]) -> Callable[..., Callable[P, R]]:
    """Decorator does nothing but casts the original function to match the given function signature"""

    @functools.wraps(func, updated=())
    def _cast_func(_func: Callable[..., Any]) -> Callable[P, R]:
        return cast(Callable[P, R], _func)

    if inspect.isfunction(func):
        return _cast_func

    raise RuntimeError("You must pass a function to this decorator.")
