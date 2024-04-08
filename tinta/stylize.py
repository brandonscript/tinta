# Originally published as AnsiColors
# Copyright (c) 2012 Giorgos Verigakis <verigak@gmail.com>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# This module is a modified version of the original AnsiColors module, and further
# modified by github.com/brandoncript to be used in the Tinta project. It is
# distributed under the same license as the original module, as well as the
# MIT License.

import re
from typing import (
    Any,
    cast,
    List,
    Optional,
    overload,
    Tuple,
    TYPE_CHECKING,
    Union,
)

from .constants import ANSI_RESET, ANSI_RESET_OCT, ANSI_STYLES, ANSI_STYLES_OFF, SEP
from .typ import InvalidStyleError

if TYPE_CHECKING:
    from .tinta import Tinta


def was_reset(s: str) -> bool:
    return s.strip().endswith(ANSI_RESET) or s.endswith(ANSI_RESET_OCT)


def ensure_reset(s: str, np: "Union[Tinta.Part, None]" = None) -> str:
    if was_reset(s) or (np and np.has_formatting):
        return s
    last_char_idx = len(s.rstrip())
    return f"{s[:last_char_idx]}{ANSI_RESET}{s[last_char_idx:]}"


def _parse_rgb(s: str) -> Tuple[int, ...]:
    if not isinstance(s, str):
        raise ValueError(f"Could not parse color '{s}'")
    s = s.strip().replace(" ", "").lower()

    # 6-digit hex
    match = re.match("#([a-f0-9]{6})$", s)
    if match:
        core = match.group(1)
        return tuple(int(core[i : i + 2], 16) for i in range(0, 6, 2))

    # 3-digit hex
    match = re.match("#([a-f0-9]{3})$", s)
    if match:
        return tuple(int(c * 2, 16) for c in match.group(1))

    # rgb(x,y,z)
    match = re.match(r"rgb\((\d+,\d+,\d+)\)", s)
    if match:
        return tuple(int(v) for v in match.group(1).split(","))

    raise ValueError(f"Could not parse color '{s}'")


def _join(*values: Union[int, str]) -> str:
    """
    Join a series of values with semicolons. The values
    are either integers or strings, so stringify each for
    good measure. Worth breaking out as its own function
    because semicolon-joined lists are core to ANSI coding.
    """
    return ";".join(str(v) for v in values).strip(";").strip()


def _color_code(
    spec: Union[str, int, Tuple[int, int, int], List[int]], base: int
) -> str:
    """Workhorse of encoding a color. Give preference to named colors from
    ANSI, then to specific numeric or tuple specs. If those don't work,
    try looking up look CSS color names or parsing CSS hex and rgb color
    specifications.

    Args:
        spec: Unparsed color specification
        base (int): Either 30 or 40, signifying the base value
                    for color encoding (foreground and background respectively).
                    Low values are added directly to the base. Higher values use `
                    base + 8` (i.e. 38 or 48) then extended codes.

    Returns:
        Discovered ANSI color encoding.

    Raises:
        ValueError if cannot parse the color spec.
    """
    if isinstance(spec, str):
        spec = spec.strip().lower()

    if spec == "default" or spec == 0:
        return "0"
    elif isinstance(spec, int) and 1 <= spec <= 255:
        return _join(base + 8, 5, spec)
    elif isinstance(spec, (tuple, list)):
        return _join(base + 8, 2, _join(*spec))
    elif str(spec).startswith("#"):
        rgb = _parse_rgb(str(spec))
        # parse_rgb raises ValueError if cannot parse spec
        return _join(base + 8, 2, _join(*rgb))
    else:
        raise ValueError(f"Could not parse color '{spec}'")


def _style_name(code: int) -> str:
    try:
        return ANSI_STYLES[code]
    except IndexError:
        raise InvalidStyleError(f"Invalid style code '{code}'")


def _style_codes(style: Union[str, int]) -> Tuple[int, int]:
    if isinstance(style, str):
        style = style.lower()
    on = ANSI_STYLES.index(style) + 1
    off = next((c for i, c in ANSI_STYLES_OFF for s in i if s == style), 0)
    return on, off


def ansi_styles(style: Union[str, int]) -> Tuple[str, str]:
    """Returns ANSI on and off strings for a style name or code.

    Args:
        style (str | int): A style name or code.

    Returns:
        Tuple[str, str]: The on and off ANSI codes for the style.
    """
    on, off = _style_codes(style)
    return f"\x1b[{on}m", f"\x1b[{off}m"


def validate_styles(*styles: Union[int, str]) -> Tuple[str, ...]:
    """Validates a list of style names. If a style is not found in the ANSI
    styles, it is removed from the list.
    """

    _styles: List[Union[int, str]] = list(styles)

    if next((isinstance(s, int) for s in styles), False):
        _styles = [_style_name(int(s)) for s in _styles]

    _styles = [str(s).lower() for s in _styles]

    if not all([s in ANSI_STYLES for s in _styles]):
        available_styles = ", ".join([f"'{s}'" for s in ANSI_STYLES])
        err = f"Invalid style string '{_styles}', must be one of {available_styles}."
        raise InvalidStyleError(err)

    return cast(Tuple[str, ...], tuple(_styles))


@overload
def tint(
    instance: "Tinta", *s: Any, color: Union[str, int], sep: str = SEP
) -> "Tinta": ...


@overload
def tint(
    instance: "Tinta", color: Union[str, int], *s: Any, sep: str = SEP
) -> "Tinta": ...


def tint(instance: "Tinta", *args, **kwargs) -> "Tinta":
    """Adds segments of text colored with the specified color.
    Can be used in place of calling named color methods.

    Args:
        instance (Tinta): The Tinta instance.
        color (str | int, optional): A color name or ANSI color index. Defaults to first argument.
        *s: Any: Segments of text to add.
        sep (str, optional): Used to join strings. Defaults to ' '.

    Returns:
        self
    """
    from .tinta import Tinta

    if not isinstance(instance, Tinta):
        raise AttributeError("tint() must be called from a Tinta instance.")

    self = instance

    # check if the first argument is a known color or valid ANSI code, or comes from kwargs
    s = args
    color = kwargs.get("color", None)
    sep = kwargs.get("sep", SEP)
    if color is None:
        if not len(s) > 1:
            raise AttributeError(
                "If no color is specified, tint() requires at least two arguments."
            )
        color = s[0]
        s = s[1:]

    self.set_color(color)
    self.push(*s, sep=sep)
    return self


def stylize(
    s: Optional[str],
    lp: "Union[Tinta.Part, None]",
    mp: "Tinta.Part",
    np: "Union[Tinta.Part, None]",
) -> str:
    """Wraps a string with ANSI styles.

    Args:
        s (str): The string to format - may be plain or pre-formatted.
        lp (Tinta.Part): The previous part.
        mp (Tinta.Part): The current (middle) part.
        np (Tinta.Part): The next part.
    """

    if s is None:
        s = ""

    if not mp:
        return s

    # On
    on = ""
    if mp.has_formatting:
        if not lp or not lp.has_formatting:
            on = _join(*[_style_codes(st)[0] for st in mp.style])
        else:
            if mp.style != lp.style:
                on = _join(
                    *[_style_codes(st)[0] for st in mp.style if st not in lp.style]
                )
        if mp.color_code and (not lp or (mp.color_code != lp.color_code)):
            on = _join(on, _color_code(mp.color_code, 30))

    # Off
    off = ""
    if mp.has_formatting:
        if (
            not np
            or not np.has_formatting
            or mp.styler._force_clear
            or bool(mp.style and not np.style and mp.color_code != np.color_code)
        ):
            off = "0"
        elif mp.style != np.style:
            styles_not_in_n = [s for s in mp.style if s not in np.style]
            off = _join(
                *list(sorted(set([_style_codes(st)[1] for st in styles_not_in_n])))
            )

    # Apply formatting
    left = f"\x1b[{on}m" if on else ""
    right = f"\x1b[{off}m" if off else ""

    last_char_idx = len(s.rstrip())

    return f"{left}{s[:last_char_idx]}{right}{s[last_char_idx:]}"


def is_ansi_str(s: str) -> bool:
    return s.startswith("\x1b[") or s.startswith("\033[")


def ansi_color_to_int(s: str) -> int:
    """Converts an ANSI escape sequence to a base 10 integer. Accepts both octal and decimal sequences, and from 1 to 3 segments separated by semicolons."""

    if not is_ansi_str(s):
        raise ValueError(f"String '{s}' is not an ANSI escape sequence.")

    if s.startswith("\x1b["):
        s = s[2:]
    elif s.startswith("\033["):
        s = s[3:]

    if s.endswith("m"):
        s = s[:-1]

    seg = s.split(";")
    if len(seg) >= 3:
        ch = seg[-3]
        if ch == "38" or ch == "48":
            return int(seg[-1])
        return int(seg[-1])

    raise ValueError(f"Could not parse ANSI escape sequence '{s}'")
