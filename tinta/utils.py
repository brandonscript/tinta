from functools import reduce
from typing import cast, List, Sequence

from .multi_version_imports import TypeVar

T = TypeVar("T")


def flatmap(lst: Sequence[List[T]]) -> List[T]:
    """Flattens a list of lists into a single list. If the list is already flat,
    it is returned as is.
    """

    # if lst is not a nested list, return it as is
    if not any(isinstance(i, list) for i in lst):
        return cast(List[T], lst)

    return reduce(list.__add__, lst)
