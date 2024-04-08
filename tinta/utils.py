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


INDENT = 0


# def measure(func):

#     import tinta.constants as C

#     @wraps(func)
#     def timeit_wrapper(*args, **kwargs):
#         global INDENT
#         class_name = args[0].__class__.__name__ if args else ""
#         if class_name == "NoneType":
#             class_name = ""
#         n = f"{INDENT * ' '}{class_name} {func.__name__}"
#         print(n)
#         start_time = time.perf_counter()
#         INDENT += 2
#         result = func(*args, **kwargs)
#         end_time = time.perf_counter()
#         total_time = (end_time - start_time) * 1000
#         INDENT -= 2
#         # if total_time > 0.00001:
#         s = f"{n} - took {total_time:.2f} ms"
#         if total_time > 0.07:
#             col = "\x1b[38;5;196m"
#         elif total_time > 0.05:
#             col = "\x1b[38;5;208m"
#         elif total_time > 0.02:
#             col = "\x1b[38;5;220m"
#         else:
#             col = "\x1b[2;38;5;237m"
#         s = f"{col}{s}\x1b[0m" if col else s
#         print(s)
#         return result

#     return timeit_wrapper if C.PERF_MEASURE else func
