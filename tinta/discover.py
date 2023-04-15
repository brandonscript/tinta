#!/usr/bin/env python

# Tinta
# Copyright 2023 github.com/brandoncript

# This program is bound to the Hippocratic License 2.1
# Full text is available here:
# https://firstdonoharm.dev/version/2/1/license

# Further to adherence to the Hippocratic Licenese, permission is hereby
# granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software") under the terms of the
# MIT License to deal in the Software without restriction, including without
# limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and / or sell copies of the Software, and to permit persons
# to whom the Software is furnished to do so, subject to the conditions layed
# out in the MIT License.

# Where a conflict or dispute would arise between these two licenses, HLv2.1
# shall take precedence.

"""This discover module is used to discover the colors available on your system.

Borrowing design from https://github.com/fidian/ansi

    Standard:    0   1   2   3   4   5   6   7
    Bright:      8   9  10  11  12  13  14  15

        16   17   18   19   20   21      34   35   36   37   38   39
        52   53   54   55   56   57      70   71   72   73   74   75
        88   89   90   91   92   93     106  107  108  109  110  111
        124  125  126  127  128  129     142  143  144  145  146  147
        160  161  162  163  164  165     178  179  180  181  182  183
        196  197  198  199  200  201     214  215  216  217  218  219

        22   23   24   25   26   27      40   41   42   43   44   45
        58   59   60   61   62   63      76   77   78   79   80   81
        94   95   96   97   98   99     112  113  114  115  116  117
        130  131  132  133  134  135     148  149  150  151  152  153
        166  167  168  169  170  171     184  185  186  187  188  189
        202  203  204  205  206  207     220  221  222  223  224  225

        28   29   30   31   32   33      46   47   48   49   50   51
        64   65   66   67   68   69      82   83   84   85   86   87
        100  101  102  103  104  105     118  119  120  121  122  123
        136  137  138  139  140  141     154  155  156  157  158  159
        172  173  174  175  176  177     190  191  192  193  194  195
        208  209  210  211  212  213     226  227  228  229  230  231

    Greyscale:  232   233   234   235   236   237   238   239   240   241   242   243   
                244   245   246   247   248   249   250   251   252   253   254   255
"""

from typing import Iterable, List, TypeVar, Union

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

color_sets = {
    'standard': [0, 1, 2, 3, 4, 5, 6, 7],
    'bright': [8, 9, 10, 11, 12, 13, 14, 15],
    'dark': {
        'greyscale': [
            232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243],
        'color1': [
            [16, 17, 18, 19, 20, 21],
            [52, 53, 54, 55, 56, 57],
            [88, 89, 90, 91, 92, 93],
            [124, 125, 126, 127, 128, 129],
            [160, 161, 162, 163, 164, 165],
            [196, 197, 198, 199, 200, 201]
        ],
        'color2': [
            [22, 23, 24, 25, 26, 27],
            [58, 59, 60, 61, 62, 63],
            [94, 95, 96, 97, 98, 99],
            [130, 131, 132, 133, 134, 135],
            [166, 167, 168, 169, 170, 171],
            [202, 203, 204, 205, 206, 207]
        ],
        'color3': [
            [28, 29, 30, 31, 32, 33],
            [64, 65, 66, 67, 68, 69],
            [100, 101, 102, 103, 104, 105],
            [136, 137, 138, 139, 140, 141],
            [172, 173, 174, 175, 176, 177],
            [208, 209, 210, 211, 212, 213]
        ]
    },
    'light': {
        'greyscale': [244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255],
        'color1': [
            [34, 35, 36, 37, 38, 39],
            [70, 71, 72, 73, 74, 75],
            [106, 107, 108, 109, 110, 111],
            [142, 143, 144, 145, 146, 147],
            [178, 179, 180, 181, 182, 183],
            [214, 215, 216, 217, 218, 219]
        ],
        'color2': [
            [40, 41, 42, 43, 44, 45],
            [76, 77, 78, 79, 80, 81],
            [112, 113, 114, 115, 116, 117],
            [148, 149, 150, 151, 152, 153],
            [184, 185, 186, 187, 188, 189],
            [220, 221, 222, 223, 224, 225]
        ],
        'color3': [
            [46, 47, 48, 49, 50, 51],
            [82, 83, 84, 85, 86, 87],
            [118, 119, 120, 121, 122, 123],
            [154, 155, 156, 157, 158, 159],
            [190, 191, 192, 193, 194, 195],
            [226, 227, 228, 229, 230, 231]
        ]
    }
}

T = TypeVar('T')


def flatten(lst: Union[List[T], List[List[T]]]) -> List[T]:
    """Flattens a list of lists into a single list. If the list is already flat,
    it is returned as is.
    """

    flattened = []
    for item in lst:
        if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
            for sub_x in flatten(item):  # type: ignore
                flattened.append(sub_x)
        else:
            flattened.append(item)
    return flattened


def is_dark(code: int) -> bool:
    """Returns True if the given color is a dark color, False otherwise.
    """
    dark_colors = sorted(flatten(color_sets['dark']['color1']) +
                         flatten(color_sets['dark']['color2']) +
                         flatten(color_sets['dark']['color3']) +
                         color_sets['dark']['greyscale'] + [0, 1, 2, 3, 4, 5, 6, 8, 9])

    return code in dark_colors


def colorbox(code: int, background: bool = False) -> str:
    """Returns a padded, styled box for the given color. If the color is 
    too dark, the text is white, otherwise dark grey.
    """

    # if color is too dark, use white text, otherwise black
    text_color = 15 if is_dark(code) else 0

    text = f"{str(code).rjust(4)} "

    if background:
        return f'\033[0m\033[48;5;{code}m\033[38;5;{text_color}m{text}\033[0m'
    else:
        return f'\033[0m\033[38;5;{code}m{text}\033[0m'


def discover(background: bool = False):
    """Prints all 256 colors in a matrix on your system."""

    print("Standard: ", end='')
    for col in color_sets['standard']:
        print(colorbox(col, background), end='')

    print("\nBright:   ", end='')
    for col in color_sets['bright']:
        print(colorbox(col, background), end='')

    print("\n")

    def print_row(brightness: Literal["light", "dark"], cset: int, row: int, i: int):
        cset_key = 'color' + str(cset)
        col = (row * 6) + i
        print(colorbox(
            flatten(color_sets[brightness][cset_key])[col], background), end='')

    for cset in range(1, 4):
        # printing 18 lines of colors:
        # [16, 17, 18, 19, 20, 21]   [34, 35, 36, 37, 38, 39]
        # [52, 53, 54, 55, 56, 57]   [70, 71, 72, 73, 74, 75]
        # .. etc. for the other 4 color sets

        for row in range(6):
            for i in range(6):
                print_row('dark', cset, row, i)
            print(str().rjust(1 if background else 4), end='')
            for i in range(6):
                print_row('light', cset, row, i)
            print("")
        print("")

    print("Greyscale: ", end='')
    for grey in color_sets['dark']['greyscale']:
        print(colorbox(grey, background), end='')

    print("\n           ", end='')
    for grey in color_sets['light']['greyscale']:
        print(colorbox(grey, background), end='')

    print("\n")
