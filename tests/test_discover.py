import pytest

from tinta.discover import color_sets, discover, is_dark


class TestDiscover():

    def test_is_dark(self):

        dark_colors = [
            *color_sets['dark']['color1'],
            *color_sets['dark']['color2'],
            *color_sets['dark']['color3'],
            *color_sets['dark']['greyscale'],
        ]

        light_colors = [
            *color_sets['light']['color1'],
            *color_sets['light']['color2'],
            *color_sets['light']['color3'],
            *color_sets['light']['greyscale'],
        ]

        addl_dark_colors = [0, 1, 4, 5, 8, 9]

        for c in dark_colors + addl_dark_colors:
            assert is_dark(c)

        for c in light_colors:
            assert not is_dark(c)

    def test_discover(self):

        print("Testing discover()...")
        discover(background=False)

        print("Testing discover(background=True)...")
        discover(background=True)
