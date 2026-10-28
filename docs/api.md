# Tinta API guide

Requires Python 3.10 or later. Install with `pip install tinta`.

## Build colored output

Color and style methods operate on a `Tinta` instance and return that instance.
`print()` writes the output and returns `None`; `to_str()` returns a string.

```python
from tinta import Tinta

t = Tinta().green("Hello").bold("world")
assert t.to_str(plaintext=True) == "Hello world"
assert t.to_str(plaintext=True) == "Hello world"  # Rendering preserves segments.
t.print(plaintext=True)
assert t.to_str() == ""  # Printing clears segments and styling.
```

## Method signatures and return values

`SEP` defaults to a space or `TINTA_SEPARATOR`. `SMART_FIX_PUNCTUATION` defaults
to true or the parsed `TINTA_SMART_FIX_PUNCTUATION` value, both read at import time.

| Method | Result and behavior |
| --- | --- |
| `Tinta(*s, color=0, styles=[], sep=SEP)` | Creates an instance containing the supplied segments. |
| `t(*s, sep=SEP)` / `t.push(*s, sep=SEP)` | Returns `t`; appends segments using the current style. |
| `t.green(*s, sep=SEP)` | Returns `t`; applies a named palette color. Other loaded color names work the same way. |
| `t.tint(*s, color=name_or_code, sep=SEP)` | Returns `t`; applies a color name or integer ANSI index. |
| `t.tint(name_or_code, *s, sep=SEP)` | Returns `t`; positional form of the same operation. |
| `t.bold(*s, sep=SEP)` / `t.b(...)` | Returns `t`; enables bold. |
| `t.underline(*s, sep=SEP)` / `t.u(...)` / `t._(...)` | Returns `t`; enables underline. |
| `t.dim(*s, sep=SEP)` | Returns `t`; enables dim styling. |
| `t.normal(*s, sep=SEP)` | Returns `t`; clears styles, preserving color. |
| `t.clear(*s, sep=SEP)` | Returns `t`; clears color and styles for subsequent segments. Existing segments remain. |
| `t.pop(qty=1)` | Returns `t`; removes up to `qty` trailing segments. |
| `t.nl(*s, sep=SEP)` | Returns `t`; prefixes the supplied text with a newline. |
| `t.to_str(sep=None, plaintext=False, escape_ansi=False, fix_punctuation=SMART_FIX_PUNCTUATION)` | Returns `str` without clearing segments. `plaintext` takes precedence over `escape_ansi`. |
| `t.print(sep=None, end="\n", file=None, flush=False, plaintext=False, force=False)` | Returns `None`. Writes and then clears segments and styling; when stealth suppresses output, the instance is preserved. |
| `Tinta.load_colors(path, typings_out=None)` | Returns `None`; replaces the shared palette, optionally writing a typed subclass module. Call before creating instances. |
| `Tinta.discover(background=False)` | Returns `None`; prints the terminal color chart. |

For `print()` and `to_str()`, `sep=None` preserves each segment's separator.
`file=None` uses the current `sys.stdout`, including stdout redirections.
`print()` supports `force=True` to override stealth. Add text with builder methods
before printing. Use `to_str()` for `escape_ansi` or per-call `fix_punctuation`.

## Explicit colors and newlines

```python
from tinta import Tinta

t = Tinta().tint("green", "Hello").nl("world")
assert t.to_str(plaintext=True) == "Hello\nworld"
t.print()
Tinta().tint("Hello", color=42).print()
```

## Write to a stream

```python
from io import StringIO
from tinta import Tinta

output = StringIO()
result = Tinta("Hello").print(file=output, plaintext=True, end="!")
assert result is None
assert output.getvalue() == "Hello!"
```

## Custom colors and typing

`Tinta.load_colors()` replaces the shared palette rather than merging it. Load
colors before creating instances. Keep any bundled colors you need in your own
file. Color names must not conflict with API names such as `print` or `bold`, or
start with an underscore. Use valid Python identifiers for generated methods.

Create `colors.ini`:

```ini
[colors]
viridian = 42
```

Generate a typed subclass for mypy and pyright:

```bash
python -m tinta codegen colors.ini -o tinta_colors.py
```

```python
from tinta_colors import Tinta

Tinta.load_colors("colors.ini")
Tinta().viridian("Hello").print()
```

Alternatively, generate the module while loading colors:

```python
from tinta import Tinta

Tinta.load_colors("colors.ini", typings_out="tinta_colors.py")
```

Import the generated subclass to obtain typed custom methods. Regenerate it when
colors change. Bundled colors already have type hints. Gray/grey aliases are
provided for matching palette names.

## Environment settings

Set these before importing `tinta`. Boolean true values are `true`, `1`, `t`, `y`,
and `yes`, case-insensitive. All other values are false.

| Variable | Default | Effect |
| --- | --- | --- |
| `TINTA_STEALTH` | false | Suppresses printing unless `force=True`. |
| `TINTA_PLAINTEXT` | false | Makes `print()` omit ANSI formatting. Use `to_str(plaintext=True)` explicitly when rendering a plain string. |
| `TINTA_SEPARATOR` | one space | Default string between segments. |
| `TINTA_SMART_FIX_PUNCTUATION` | true | Controls automatic punctuation spacing. Override per call with `to_str(fix_punctuation=...)`. |
