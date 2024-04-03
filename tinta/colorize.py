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
from typing import Any, List, Optional, overload, Tuple, TYPE_CHECKING, Union

from .constants import ANSI_RESET_HEX, ANSI_RESET_OCT, SEP
from .typ import MissingColorError

if TYPE_CHECKING:
    from .tinta import Tinta

STYLES = (
    "none",
    "bold",
    "faint",
    "italic",
    "underline",
    "blink",
    "blink2",
    "negative",
    "concealed",
    "crossed",
)


def was_reset(s: str) -> bool:
    return s.strip().endswith(ANSI_RESET_HEX) or s.endswith(ANSI_RESET_OCT)


def ensure_reset(s: str) -> str:
    if was_reset(s):
        return s
    last_char_idx = len(s.rstrip())
    return f"{s[:last_char_idx]}{ANSI_RESET_HEX}{s[last_char_idx:]}"


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
    return ";".join(str(v) for v in values)


def _color_code(
    spec: Union[str, int, Tuple[int, int, int], List[int]], base: int
) -> str:
    """
    Workhorse of encoding a color. Give preference to named colors from
    ANSI, then to specific numeric or tuple specs. If those don't work,
    try looking up look CSS color names or parsing CSS hex and rgb color
    specifications.

    :param spec: Unparsed color specification
    :param base: Either 30 or 40, signifying the base value
        for color encoding (foreground and background respectively).
        Low values are added directly to the base. Higher values use `
        base + 8` (i.e. 38 or 48) then extended codes.
    :returns: Discovered ANSI color encoding.
    :raises: ValueError if cannot parse the color spec.
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


def colorize(
    s: str,
    fg: Optional[int] = None,
    bg: Optional[int] = None,
    style: Optional[str] = None,
    reset: bool = False,
) -> str:
    """
    Add ANSI colors and styles to a string.

    Args:
    s: String to format.
    fg: Foreground color specification.
    bg: Background color specification.
    style: Style names, separated by '+'
    reset: Whether to reset the formatting at the end of the string. Default is False.

    Returns: Formatted string.
    """
    codes: List[str] = []

    if fg is not None:
        codes.append(_color_code(fg, 30))
    # TODO: Background is not implemented
    # if bg is not None:
    #     codes.append(_color_code(bg, 40))
    if style is not None:
        for style_part in style.split("+"):
            if style_part in STYLES:
                codes.append(str(STYLES.index(style_part)))
            else:
                raise ValueError(f'Invalid style "{style_part}"')

    if codes:
        template = "\x1b[{0}m{1}"
        if reset:
            template += ANSI_RESET_HEX
        return template.format(_join(*codes), s)
    else:
        return s


@overload
def tint(
    instance: "Tinta", *s: Any, color: Union[str, int], sep: str = SEP
) -> "Tinta": ...


@overload
def tint(
    instance: "Tinta", color: Union[str, int], *s: Any, sep: str = SEP
) -> "Tinta": ...


# pylint: disable=redefined-outer-name
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

    # color: Optional[Union[str, int]] = None, *s: Any, sep: str = SEP

    # check if the first argument is a known color or valid ANSI code, or comes from kwargs
    self = instance
    s = args
    color = kwargs.get("color", None)
    sep = kwargs.get("sep", SEP)
    if color is None:
        if not len(s) > 1:
            raise AttributeError(
                "If no color is specified, tint() requires at least two arguments."
            )
        if args and isinstance(args[0], (str, int)):
            color = s[0]
            s = s[1:]
        else:
            raise AttributeError(
                "Could not determine color from arguments. Either pass a color as the first argument, or use the color keyword argument."
            )

    # if color is numeric integer string, assume it's an ANSI color code
    if isinstance(color, int) or (isinstance(color, str) and color.isdigit()):
        self.color = int(color)

    # Check if color_name is a valid color if color is a string
    if isinstance(color, str):
        if not hasattr(self.colors, color):  # type: ignore
            raise MissingColorError(
                f"Invalid color name: {color}. Is it in colors.ini?"
            )
        self.color = self.colors.get(color)  # type: ignore

    self.push(*s, sep=sep)
    return self
