## Tinta

<img width="200" alt="Tinta Logo" src="https://user-images.githubusercontent.com/1480253/118584629-38023b80-b74c-11eb-8511-05258af553fb.png" />

Tinta is a magical console output tool with support for printing in beautiful colors and with rich formatting, like bold and underline, using chainable instance methods. It's so pretty, it's almost like a unicorn!

![version](https://img.shields.io/badge/version-1.1.1-green.svg) [_![GitHub Actions Badge](https://img.shields.io/github/actions/workflow/status/brandonscript/tinta/run-tests.yml)_](https://github.com/brandonscript/tinta/actions) [_![Codacy Badge](https://app.codacy.com/project/badge/Grade/32bf3e3172cf434b914647f06569a836)_](https://www.codacy.com/gh/brandonscript/tinta/dashboard?utm_source=github.com&utm_medium=referral&utm_content=brandonscript/tinta&utm_campaign=Badge_Grade) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tinta) [![PyPI downloads](https://img.shields.io/pypi/dm/tinta)](https://pypi.org/project/tinta/) [![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [_![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.0-4baaaa.svg)_](CODE_OF_CONDUCT.md)

## Features and Tinta Basics

`Tinta` takes a statically typed approach to handling rich-color console output.

In the past you might have fiddled with ANSI colors codes, or passed strings to a generic class, only to discover you typo'd one of them! (Yes, we've all been there).

But with `Tinta`, you can create your own `colors.ini` file, which dynamically generates builder pattern methods for `Tinta`. If you add a color for `wine` to your colors file, you can then use:

```python
from tinta import Tinta
Tinta.load_colors('colors.ini')
Tinta().wine('sip')
```

For mypy/pyright support of custom colors, generate a typed subclass with `python -m tinta codegen` (see below).
You can make a really simple drop-in `print()` replacement:

```python
Tinta('Our neural pathways have become accustomed '\
      'to your sensory input patterns.').print()
```

Or you can create a variable to make things easier to read (or use control flows):

```python
from tinta import Tinta

children = True

t = Tinta().mint('Fate.')
t.dark_gray('It protects')
t.underline().red('fools')

if children:
    t.normal().pink('little children')
else:
    t.normal().yellow('spotted cats')

t.dark_gray(', and ships named')
t.mint("Enterprise.").print()
```

**_OK, neat, so how is that like unicorns?_**

Glad you asked! Here are some pretty pictures:

<img width="600" alt="Unicorns" src="https://user-images.githubusercontent.com/1480253/118717080-70e8f180-b7da-11eb-8ce8-08fe837fe73f.png" />
<br>
<img width="600" alt="Starbase" src="https://user-images.githubusercontent.com/1480253/118717091-734b4b80-b7da-11eb-9ecc-5cae5888878b.png" />

## Installation and Getting Started

Requires **Python 3.10 or later**.

### Install Tinta

```bash
pip install tinta
```

(Or visit https://pypi.org/project/tinta/)

### Add Tinta to your project

```python
from tinta import Tinta

Tinta('Elementary, my dear!').print()
```

### Create a `colors.ini` file

An example `colors.ini` file might look like:

```ini
# A list of ansi colors for your console.
[colors]
green = 35
red = 1
blue = 32
yellow = 214
viridian = 42
```

Or modify the `Tinta` colors.ini from [_here_](https://github.com/brandonscript/tinta/blob/main/tinta/colors.ini).

You can configure a path to your `colors.ini` file. This path can be relative, or absolute; the best way to make a path is using `pathlib.Path()`. Tinta will try and find the file in the current working directory, or you can specify a path:

```python
from pathlib import Path
from tinta import Tinta
Tinta.load_colors(Path().cwd() / 'config/colors.ini')
```

> **Note:** `Tinta.load_colors()` **replaces** the active color map (it does not merge with the defaults). If your project ini only defines `blue`, `mint`, and `viridian`, only those color methods are available after loading.

### Typed custom colors (mypy / pyright)

Default colors from Tinta's bundled `colors.ini` are typed out of the box (`Tinta().mint(...)` type-checks).

For **custom** colors in your own `colors.ini`, generate a typed subclass so editors and type checkers recognize methods like `.viridian()` without `# type: ignore`:

```bash
python -m tinta codegen path/to/colors.ini -o path/to/tinta_colors.py
```

```python
from path.to.tinta_colors import Tinta  # generated subclass

Tinta.load_colors("path/to/colors.ini")
Tinta().viridian("hello").print()
```

You can also write the typed module when loading colors:

```python
Tinta.load_colors("path/to/colors.ini", typings_out="path/to/tinta_colors.py")
```

Regenerate the typed module whenever you add or rename colors in your ini.

### Customizing your colors

You can use `Tinta.discover()` to discover what colors are available on your console.

```python
Tinta.discover()
# or to show the colors in the background
Tinta.discover(background=True)
```

<img src="https://github.com/brandonscript/tinta/blob/main/examples/tinta-discover.png?raw=true" style="max-width: 540px; !important" width="540" alt="Tinta.discover() output, a set of ANSI color-coded numbers in the terminal" />

## Tinta Basics

```python
from tinta import Tinta

Tinta('Unicorns are soft').print()
# prints: Unicorns are soft in plain text

Tinta('Unicorns are soft').pink().print()
# prints: Unicorns are soft in pink

Tinta('Unicorns are soft').pink().bold().print()
# prints: Unicorns are soft in bold pink

# You can chain as many methods as you want, and you can instantiate a single Tinta object
t = Tinta()
t.pink('Unicorns are soft, and').bold('very').normal('kind.')
t.print()
Tinta().pink('Unicorns are soft, and').bold('very').normal('kind.').print()
# prints: Unicorns are soft, and very kind.
#         [--------pink--------][bold][normal]

# Notice how spaces are preserved between segments?
# You can change this with the sep arg:
Tinta().pink('Unicorns are soft, and', sep="").bold('very', sep="").normal('kind.').print()
# prints: Unicorns are soft,andvery kind.
# or...
Tinta().pink('Unicorns are soft, and').bold('very').normal('kind.').print(sep="")
# prints: Unicorns are soft, andverykind.

# Tinta will also try and automatically fix common punctuation issues that can occur when segments are joined together:
Tinta().pink('Unicorns are soft, and').purple(", you know,").bold('very').normal(', very, kind.').print()
# With smart fixing disabled, this would normally print:
# > Unicorns are soft, and , you know, very , very, kind.

# But with smart fixing enabled, it prints correctly:
# > Unicorns are soft, and, you know, very, very, kind.

# This is turned on by default, but you can disable this by setting TINTA_SMART_FIX_PUNCTUATION to `false` in your environment.
```

You can run the examples in the `examples/` directory to see more:

```bash
# check out the repo
git clone https://github.com/brandonscript/tinta.git
cd tinta
python examples/basic_example.py
```

## API Reference

See the [API guide](docs/api.md) for signatures, return values, and complete examples.

### Tinta (+ color methods)

#### Dynamic methods

These methods are loaded dynamically from your `colors.ini` file at runtime:

```python
Tinta().green()
Tinta().red()
Tinta().blue()
Tinta().wine()
Tinta().my_color()
# etc.
```

Default bundled colors are declared on `Tinta` for type checkers. For custom project colors, generate a typed subclass with `python -m tinta codegen` (see [Typed custom colors](#typed-custom-colors-mypy--pyright) above). You can always use `Tinta().tint(<color>, text)` as an alternative to named color methods. Color and style methods require a `Tinta` instance.

### Common Args

All "add" methods (each color and style method, `Tinta()`, `push()`, and `tint`) take the following common args:

- `s (str)` – A sequence of one or more text strings, to be joined together.
- `sep (str)` – Used to join segment strings. Defaults to `' '`.
  > _Note: `sep` behavior has been changed in v0.1.7 - if passing a `sep` argument in `print()`, it will overwrite any segment's individual `sep` argument._

For example:

```python
Tinta('A set', 'of strings', 'joined', 'with', 'semicolons', sep=';').print()
```

```bash
~ » A set;of strings;joined;with;semicolons
```

(or)

```python
Tinta('A set', 'of strings', 'joined', 'with', 'double spaces').print(sep='  ')
```

```bash
~ » A set  of strings  joined  with  double spaces
```

### Attributes

All `Tinta` and dynamic color methods will make available the following attributes:

- `color (str)` — The current color name, e.g. `'white'`; use `color_code` for its integer ANSI index.
- `style (list[str])` — Active style names, e.g. `['bold', 'underline']`.
- `parts (list)` — A list of `Tinta.Part` segments, which expose `pln`, `fmt(...)`, and `esc(...)`.
- `parts_pln (list[str])` — The plain text of each segment.

### Built-in Methods

_See below for detailed usage and arguments._

> (Note: breaking changes in v0.1.7 - several methods have been renamed for better semantics).

- `print()` – Prints to the console.
- `to_str() -> str` – Returns a joined text string.
- `discover()` – Prints a list of available colors to the console.

Remember, all of the following methods return the current `Tinta` instance `-> self` so you can chain styles together:

- `()` or `push()` – Adds another segment using the previous style. Replaces `add()`.
- `pop()` – Removes the last segment. This is useful if you want to remove a segment that was added with `push()`.
- `tint()` – Behaves like `.push()`, but adds segments using the specified color string or ANSI code. Replaces `code()`.
- `nl()` – Appends the contents preceded by a newline char (`\n`). Renamed from `line()`.
- `clear()` – Clears all styling for the next segment so it uses terminal default styling. Replaces `reset()`.

- `b()` or `bold()` – Adds a **bold** segment.
- `_()` or `u()` or `underline()` – Adds an ~underlined~ segment.
- `dim()` – Adds a darker, dimmed segment.
- `normal()` – Resets the style, but retains any active color.

#### `print()`

Prints to the console. Probably the most important method, because if you don't print, you don't see anything at all!
A good first step in troubleshooting is checking that you remembered to `print()` (ask me how I know...)

`print(sep=None, end="\n", file=None, flush=False, plaintext=False, force=False)` writes the current segments and returns `None`.

- `sep` overrides segment separators; `None` preserves each segment's separator.
- `end`, `file`, and `flush` have the same purpose as in Python's built-in `print()`.
- `plaintext=True` prints without ANSI formatting.
- `force=True` prints even when `TINTA_STEALTH` is enabled.

Add text with `push()` or another builder method before calling `print()`:

```python
from tinta import Tinta

Tinta().purple("Is it a bird?").push("No, maybe it's a...").print(plaintext=True)
Tinta().green('Plane?').print(force=True)
```

For escaped ANSI output or per-call punctuation control, use `to_str()` instead.

It's also important to note that `print()` doesn't make a variable unusable, but it will reset and remove all styles and previous segments. This means you can do:

```python
t = Tinta()

t.blue('A cloud').print()
t.green('An old, wise, and very small alien').print()
```

#### `to_str()`

> _Previously `text()`_

`to_str(sep=None, plaintext=False, escape_ansi=False, fix_punctuation=SMART_FIX_PUNCTUATION) -> str` returns the current segments as a string without clearing them.

- `sep=None` preserves segment separators; a string overrides them.
- `plaintext=True` removes ANSI formatting.
- `escape_ansi=True` escapes ANSI control characters for inspection. `plaintext` takes precedence.
- `fix_punctuation` controls punctuation spacing for this call; its default comes from `TINTA_SMART_FIX_PUNCTUATION`.

```python
from tinta import Tinta

t = Tinta().green("Hello").bold("world")
assert t.to_str(plaintext=True) == "Hello world"
escaped = t.to_str(escape_ansi=True)
```

#### `()` or `push()`

> _Previously_ `add()`

Sometimes you want the convenience of readability without changing styles, or you might want to use control flow to set a variable. For these, you can directly chain any `Tinta` object via its `__call__` method, or via `push()`:

```python
t = Tinta().gray('I am a bear')
if you_love_bears:
    t.pink('and I love bears!')
else:
    t('but I am sad.')
    # or
    t.push('but I am sad.')
t.print()

Tinta().amber('I')('am an amber bear').black(', and I am a')('black bear.').print()
```

#### `nl()`

Adds a text segment preceded by a newline.

```python
Tinta('A cat').nl('scratches').print()
# A cat
# scratches
```

#### `tint()`

Sometimes you might want to use a color by string name, or one that wasn't defined in your `colors.ini`. For that, you can use `tint()`.

> _Note: some of this functionality was previously in `code()`, which is now combined into `tint()`._

Just set the `color` kwarg to specify an ANSI color code or string name:

```python
Tinta().tint('A bear who knows all the answers', color=42).print()
Tinta().tint('An amber bear', color='amber').print()
```

If you don't pass a color kwarg, the first argument will be used as the color:

```python
Tinta().tint(42, 'A bear who knows all the answers').print()
Tinta().tint('amber', 'An amber bear').print()
```

## Environment Variables

Sometimes it's useful to globally configure `Tinta` on a system where you might want it to behave differently, without changing your source code. Set these variables before importing `tinta`; their values are read at import time. Boolean settings accept `true`, `1`, `t`, `y`, and `yes` (case-insensitive) as true; other values, including `false` and `0`, are false. `TINTA_SEPARATOR` is a string, not a boolean.

`TINTA_STEALTH` – Disables console output globally

`TINTA_PLAINTEXT` – Disables rich console output, only printing plain text.

`TINTA_SEPARATOR` – Changes the default separator (`' '`) to this value.

`TINTA_SMART_FIX_PUNCTUATION` – Controls smart punctuation fixing (default: `true`)

## Development Setup

Install all dev dependencies with [Poetry](https://python-poetry.org):

```bash
poetry install
```

Then run tests, lint, etc.:

```bash
poetry run pytest          # run tests
poetry run lint-check      # ruff lint check
poetry run lint-fix        # ruff lint fix
```

Builds use Hatchling (not `poetry build`):

```bash
hatchling build
```

## Contributing

Contributions are welcome! Please send in a PR with a clear explanation of what you're adding and why, and where applicable, add tests to validate. Please read our [_code of conduct_](CODE_OF_CONDUCT.md) before contributing.

## Acknowledgements

Special thanks to [_@katherinecodes_](https://twitter.com/katherinecodes) for [_readme.so_](https://readme.so/), [_@jessicaspacekat_](https://twitter.com/jessicaspacekat) for [_rikeripsum.com_](http://rikeripsum.com), and [_ansicolors_](https://github.com/jonathaneunice/colors/).

## License

Tinta is licensed under the [MIT License](LICENSE).

We encourage users to abide by the spirit of the [Hippocratic License](https://firstdonoharm.dev) and not use this software in a way that directly or indirectly causes harm. This is a request, not a license condition.
