# pylint: disable=import-error
from tinta.discover import color_sets, discover, flatmap, is_dark


class TestDiscover:

    def test_is_dark_or_light(self):

        dark_colors = [
            *flatmap(color_sets["dark"]["color1"]),  # type: ignore
            *flatmap(color_sets["dark"]["color2"]),  # type: ignore
            *flatmap(color_sets["dark"]["color3"]),  # type: ignore
            *color_sets["dark"]["greyscale"],
        ]  # type: ignore

        light_colors = [
            *flatmap(color_sets["light"]["color1"]),  # type: ignore
            *flatmap(color_sets["light"]["color2"]),  # type: ignore
            *flatmap(color_sets["light"]["color3"]),  # type: ignore
            *color_sets["light"]["greyscale"],
        ]  # type: ignore

        for col in dark_colors:
            assert is_dark(col)

        for col in light_colors:
            assert not is_dark(col)

    def test_discover(self):

        print("Testing discover()...")
        discover(background=False)

        print("Testing discover(background=True)...")
        discover(background=True)
