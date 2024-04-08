## Tinta

<img width="200" alt="Tinta Logo" src="https://user-images.githubusercontent.com/1480253/118584629-38023b80-b74c-11eb-8511-05258af553fb.png" />

Tinta is a magical console output tool with support for printing in beautiful colors and with rich formatting, like bold and underline, using static, chain-able methods. It's so pretty, it's almost like a unicorn!

![version](https://img.shields.io/badge/version-0.1.7b5-post0-green.svg) [_![GitHub Actions Badge](https://img.shields.io/github/actions/workflow/status/brandonscript/tinta/run-tests.yml)_](https://github.com/brandonscript/tinta/actions) [_![Codacy Badge](https://app.codacy.com/project/badge/Grade/32bf3e3172cf434b914647f06569a836)_](https://www.codacy.com/gh/brandonscript/tinta/dashboard?utm_source=github.com&utm_medium=referral&utm_content=brandonscript/tinta&utm_campaign=Badge_Grade) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tinta) ![MIT License](https://img.shields.io/github/license/brandonscript/tinta) [_![](https://img.shields.io/badge/ethical-source-%23bb8c3c?labelColor=393162)_](https://img.shields.io/badge/ethical-source-%23bb8c3c?labelColor=393162) [_![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.0-4baaaa.svg)_](code_of_conduct.md)

## Features and Tinta Basics

`Tinta` takes a statically typed approach to handling rich-color console output.

In the past you might have fiddled with ANSI colors codes, or passed strings to a generic class, only to discover you typo'd one of them! (Yes, we've all been there).

But with `Tinta`, you can create your own `colors.ini` file, which dynamically generates builder pattern methods for `Tinta`. If you add a color for `wine` to your colors file, you can then use:

```python
from tinta import Tinta
Tinta.load_colors('colors.ini')
Tinta().wine('sip')
```

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
green: 35
red: 1
blue: 32
yellow: 214
```

Or modify the `Tinta` colors.ini from [_here_](https://github.com/brandonscript/tinta/blob/main/tinta/colors.ini).

You can configure a path to your `colors.ini` file. This path can be relative, or absolute; the best way to make a path is using `pathlib.Path()`. Tinta will try and find the file in the current working directory, or you can specify a path:

```python
from pathlib import Path
from tinta import Tinta
Tinta.load_colors(Path().cwd() / 'config/colors.ini')
```

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

### Tinta (+ color methods)

#### Dynamic methods

These methods are loaded dynamically from your `colors.ini` file:

```python
Tinta().green()
Tinta().red()
Tinta().blue()
Tinta().wine()
Tinta().my_color()
# etc.
```

A note on linters like Pylance or pylint: these methods are dynamically generated, so they won't be recognized by your linter as built-in methods. Until Python natively supports type definitions for dynamically generated code, you may have to suppress these warnings:

```python
# pyright: reportGeneralTypeIssues=false
Tinta().green() # or
# pylint: disable=no-member
Tinta().green()

Tinta().green() # type: ignore
```

If this is frustrating, you can always use the `Tinta.tint(<color>)` methods, which are not dynamically generated.

### Common Args

All "add" methods (each color and style method, `Tinta()`, `push()`, and `tint`) take the following common args:

- `s (str)` – A sequence of one or more text strings, to be joined together.
- `sep (str)` – Used to join segment strings. Defaults to `' '`.
  > _Note: `sep` behavior has been changed in v0.1.7b5-post0 - if passing a `sep` argument in `print()`, it will overwrite any segment's individual `sep` argument._

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

- `color (str)` — A color string or ANSI color code (int), e.g. 'white' or 42.
- `style (str)` — A style string, e.g. 'bold', 'dim', 'underline'. Multiple styles are joined with a +.
- `parts (list)` — A list of `Tinta.Part` segments, which each have a `fmt`, `pln`, and `esc` attribute.
- ~~`parts_plaintext (list)` — A list of unstyled text segments.~~

### Built-in Methods

_See below for detailed usage and arguments._

> (Note: breaking changes in v0.1.7b5-post0 - several methods have been renamed for better semantics).

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

This supports all the built-in Python 3 `print()` methods, too (`sep`, `end`, `file`, `flush`), as well as:

- `sep (str)` – Used to join segment strings. Defaults to `' '`.
- `plaintext (bool)` – Returns a compiled plaintext string
- `escape_ansi (bool)` – If True, escapes ANSI codes with a double \\. Defaults to `False`.
- `fix_punctuation (bool)` – If True, fixes common punctuation issues. Defaults to `True`, or the value of `'env::TINTA_SMART_FIX_PUNCTUATION'`.
  and
- `s* (str)` – You can also pass any arbitrary sequence of strings to `print()` to push additional segments.

```python
# Prints in plaintext
Tinta().purple("Is it a bird?").print("No, maybe it's a...", plaintext=True)

# Always prints, even if 'env::TINTA_STEALTH' is set)
Tinta().green('Plane?').print(force=True)
```

It's also important to note that `print()` doesn't make a variable unusable, but it will reset and remove all styles and previous segments. This means you can do:

```python
t = Tinta()

t.blue('A cloud').print()
t.green('An old, wise, and very small alien').print()
```

#### `to_str()`

> _Previously `text()`_

Constructs the string that would be sent to `print()`, but returns it instead of printing it. Accepts all the same arguments as `print()` except `file` and `flush`.

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

Tinta().brown('I')('am a brown bear').black(', and I am a')('black bear.').print()
```

#### `nl()`

Adds a text segment preceded by a newline.

```python
Tinta('A cat').line('scratches').print()
# A cat
# scratches
```

#### `tint()`

Sometimes you might want to use a color by string name, or one that wasn't defined in your `colors.ini`. For that, you can use `tint()`.

> _Note: some of this functionality was previously in `code()`, which is now combined into `tint()`._

Just set the `color` kwarg to specify an ANSI color code or string name:

```python
Tinta().tint('A bear who knows all the answers', color=42).print()
Tinta().tint('A brown bear', color='brown').print()
```

If you don't pass a color kwarg, the first argument will be used as the color:

```python
Tinta().tint(42, 'A bear who knows all the answers').print()
Tinta().tint('brown', 'A brown bear').print()
```

## Environment Variables

Sometimes it's useful to globally configure `Tinta` on a system where you might want it to behave differently, without changing your source code. If these Environment variables are present on the system, they will be considered True.

`TINTA_STEALTH` – Disables console output globally

`TINTA_PLAINTEXT` – Disables rich console output, only printing plain text.

`TINTA_SEPARATOR` – Changes the default separator (`' '`) to this value.

`TINTA_SMART_FIX_PUNCTUATION` – Controls smart punctuation fixing (default: `true`)

## Running Tests

To run tests, run the following command:

```bash
pip install pytest
python -m pytest -v
```

## Contributing

Contributions are welcome! Please send in a PR with a clear explanation of what you're adding and why, and where applicable, add tests to validate. Please read our [_code of conduct_](CODE_OF_CONDUCT.md) before contributing.

## Acknowledgements

Special thanks to [_@katherinecodes_](https://twitter.com/katherinecodes) for [_readme.so_](https://readme.so/), [_@jessicaspacekat_](https://twitter.com/jessicaspacekat) for [_rikeripsum.com_](http://rikeripsum.com), and [_ansicolors_](https://github.com/jonathaneunice/colors/).

## License

Tinta is licensed under the [_MIT License_](LICENSE). If you use this software, you must also agree under the terms of the Hippocratic License 3.0 to not use this software in a way that directly or indirectly causes harm. You can find the full text of the license at https://firstdonoharm.dev.
