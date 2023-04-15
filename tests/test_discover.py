from tinta.discover import color_sets, discover, flatten, is_dark


class TestDiscover():

    def test_is_dark(self):

        dark_colors = [
            *flatten(color_sets['dark']['color1']),
            *flatten(color_sets['dark']['color2']),
            *flatten(color_sets['dark']['color3']),
            *color_sets['dark']['greyscale'],
        ]

        light_colors = [
            *flatten(color_sets['light']['color1']),
            *flatten(color_sets['light']['color2']),
            *flatten(color_sets['light']['color3']),
            *color_sets['light']['greyscale'],
        ]

        addl_dark_colors = [0, 1, 4, 5, 8, 9]

        for col in dark_colors + addl_dark_colors:
            assert is_dark(col)

        for col in light_colors:
            assert not is_dark(col)

    def test_discover(self):

        print("Testing discover()...")
        discover(background=False)

        print("Testing discover(background=True)...")
        discover(background=True)
