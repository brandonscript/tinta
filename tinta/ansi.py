import configparser
import sys
from pathlib import Path

from .typ import MissingColorError

config = configparser.ConfigParser()


class AnsiColors:
    """Color builder for Tinta's console output.

    ANSI color map for console output. Get a list of colors here =
    http://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html#256-colors

    Or run Tinta.discover() to see all 256 colors on your system.

    You can change the colors the terminal outputs by changing the
    ANSI values in colors.ini.
    """

    def __init__(self, path: str | Path | None = None):
        path = Path(path) if path else Path(__file__).parent / "colors.ini"
        if not path.is_absolute():
            path = Path().cwd() / path
        if not path.exists():
            raise FileNotFoundError(
                f"Tinta failed to load colors, '{path}' does not exist."
            )

        # if path is a dir, look for colors.ini
        if path.is_dir():
            path = path / "colors.ini"

        # if there is still no colors.ini file, look for one in Path.cwd() or PYTHONPATH
        if not path.exists():
            for p in [Path().cwd(), Path(sys.path[0])]:
                if (p / "colors.ini").exists():
                    path = p / "colors.ini"
                    break

        if not path.exists():
            raise FileNotFoundError(
                f"Tinta failed to load colors, could not find 'colors.ini' in cwd or in PYTHONPATH. Please provide a valid path to a colors.ini file."
            )

        config.read(path)
        for k, v in config["colors"].items():
            self.__setattr__(k, int(v))

    def get(self, color: str) -> int:
        """Returns the ANSI code for a color.

        Args:
            color (str): A color name.

        Returns:
            int: The ANSI code for the color.
        """

        if color == "default":
            return 0

        if color not in config["colors"]:
            raise MissingColorError(f"Color '{color}' not found in colors.ini.")

        return int(config["colors"][color])

    def list_colors(self) -> list[str]:
        """Returns a list of all colors in the colors.ini file."""
        return list(config["colors"].keys())
