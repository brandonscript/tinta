
# Tinta

<img width="200" alt="Tinta Logo" src="https://user-images.githubusercontent.com/1480253/118584629-38023b80-b74c-11eb-8511-05258af553fb.png">

Tinta is a magical console output tool for modern Python with support for printing in beautiful 
colors and with rich formatting, like bold and underline. It's so pretty,
it's almost like a unicorn!

![version](https://img.shields.io/badge/version-0.1.0--beta-green.svg) [![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/tterb/atomic-design-ui/blob/master/LICENSEs) [![](https://img.shields.io/badge/ethical-source-%23bb8c3c?labelColor=393162)](https://img.shields.io/badge/ethical-source-%23bb8c3c?labelColor=393162) [![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.0-4baaaa.svg)](code_of_conduct.md)

## Features and Tinta Basics

Tinta takes a statically typed approach to handling rich-color console output.

In the past you might have fiddled with ANSI colors codes, or passed strings to a generic class, only to discover you typo'd one of them! (Yes, we've all been there).

But with Tinta, you can create your own `colors.yaml` file, which dynamically generates builder pattern methods for `Tinta`. If you add a color for `wine` to your colors file, you can then use:

```python
from tinta import Tinta
Tinta.load_colors('colors.yaml')
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

if chilren:
    t.normal().pink('little children')
else:
    t.normal().yellow('spotted cats')

t.dark_gray(', and ships named')
t.mint("Enterprise.").print()
```

#### OK, neat, so how is that like unicorns?

Glad you asked! Here are some pretty pictures:

<img width="500" alt="Tinta example input" src="https://user-images.githubusercontent.com/1480253/118583296-b14c5f00-b749-11eb-9854-773d01da299e.png">
<img width="500" alt="Tinta example output" src="https://user-images.githubusercontent.com/1480253/118583353-c4f7c580-b749-11eb-8606-153731c3b437.png">

## Installation and Getting Started 

Install Tinta:

```bash 
pip install tinta
```
    
Add Tinta to your project, and optionally configure a path to your `colors.yaml` file. This path can be relative, or absolute; the best way to make a path is using `pathlib.Path()`.

```python
from tinta import Tinta

# or to specify your custom colors, 
# relative to your project's cwd:

from pathlib import Path
from tinta import Tinta
Tinta.load_colors(Path().cwd() / 'config/colors.yaml')
```

To discover what colors are available on your console:

```python
Tinta.discover()
```

An example `colors.yaml` file might look like:

```yaml
# A list of ansi colors for your console.
green: 35
red: 1
blue: 32
yellow: 214
```
## API Reference

### Tinta (+ color methods)

#### Dynamic methods

These methods are loaded dynamically from your `colors.yaml` file:

```python
Tinta().green()
Tinta().red()
Tinta().blue()
Tinta().wine()
Tinta().my_color()
# etc.
```

#### Args

Each color method (and `Tinta`) supports the following args. A copy if itself is then returned for method chaining:

- `*s (str)` – A sequence of one or more text strings, to be joined together.
- `sep (str)` – Used to join segment strings. Defaults to `' '`.

For example:
```python
Tinta('A set', 'of strings', 'joined', 'with', 'semicolons', sep=';').print()
```
```bash
~ » A set;of strings;joined;with;semicolons
```

#### Attributes

All `Tinta` and dynamic color methods will make available the following attributes:

- `color (str)` — A color string or ansi color code (int), e.g. 'white' or 42.
- `style (str)` — A style string, e.g. 'bold', 'dim', 'underline'. Multiple styles are joined with a +.
- `parts (list)` — A list of richly styled text segments.
- `parts_plaintext (list)` — A list of unstyled text segments.

#### Built-in Methods

 - `print()` – Prints to the console. See below for supported args.
 - `text(sep=' ') -> str` – Returns a compiled rich text string
 - `plaintext(sep=' ') -> str` – Returns a compiled plaintext string
 - `add() -> self` – Adds segments using any previously defined styles.
 - `line() -> self` – Appends the contents preceded by a newline char (`\n`).
 - `bold() -> self` – Sets segments to bold.
 - `underline() -> self` – Sets segments to underline.
 - `dim() -> self` – Sets segments to a darker, dimmed color.
 - `code() -> self` – Adds segments using the specified ansi code. 
 - `normal() -> self` – Resets the style to default.
 - `reset() -> self` – Resets both style and color to default.

All style methods support the same arguments as `Tinta` and dynamic color methods:

```python
Tinta().underline('Underlined', 'text').print()
Tinta().bold('Bold', 'text', sep='+').print()
Tinta().dim('Dimmed', 'text', sep='_').print()
```

#### `print()`

Prints to the console. Probably the most important method, because if you don't print, you don't see anything at all! 
A good first step in troubleshooting is checking that you remembered to `print()` (ask me how I know...)

This supports all the built-in Python 3 `print()` methods, too (`sep`, `end`, `file`, `flush`), as well as:

- `plaintext (bool)` – Prints in plaintext if set to True
- `force (bool)` – Forcibily prints to the console, even if `'env::TINTA_STEALTH'` is set.

```python
# Prints in plaintext
Tinta().purple('A bird').print(plaintext=True) 

# Always prints, even if 'env::TINTA_STEALTH' is set)
Tinta().green('A plane').print(force=True) 
```

It's also important to note that `print()` doesn't make a variable unusable, it just resets and clears itself when called. This means you can do:

```python
tint = Tinta()

tint.blue('A cloud').print()
tint.green('A tree').print()
```

#### `add()`
Sometimes you want the convenience of readability without changing styles, or you might want to use control flow to set a variable. For these, you can use `add()`:

```python
tint = Tinta().gray('I am a bear')
if you_love_bears:
    tint.pink('and I love bears!')
else:
    tint.add('but I am sad.')
tint.print()
```

For example:
```python
Tinta('A set', 'of strings', 'joined', 'with', 'semicolons', sep=';').print()
```
```bash
~ » A set;of strings;joined;with;semicolons
```

#### `line()`
Adds your same text, but preceded by a newline.

```python
Tinta('A cat').line('scratches').print()
# A cat
# scratches
```

#### `code()`

Sometimes you might want to use a color that wasn't defined in your `colors.yaml`. For that, you can use `.code()`.
Just set the `code` arg to specify an ANSI color code:
```python
Tinta().code('A bear', code=42).print()
```

This is useful for adding colors on the fly if they aren't defined in `colors.yaml`.
## Environment Variables

Sometimes it's useful to globally configure `Tinta` on a system where you might want it to behave differently, without changing your source code. If these Environment variables are present on the system, they will be considered True.

`TINTA_STEALTH` – Disables console output globally

`TINTA_PLAINTEXT` – Disables rich console output, only printing plain text.

`TINTA_SEPARATOR` – Changes the default separator (`' '`) to this value.

  
## Running Tests

To run tests, run the following command:

```bash
pip install -r requirements-text.txt
```

then simply:

```bash
python -m pytest -xv
```

## Contributing

Contributions are welcome! Please send in a PR with a clear explanation of what you're adding and why, and where applicable, add tests to validate. Please read our [code of conduct](CODE_OF_CONDUCT.md) before contributing.
  
## Acknowledgements

Special thanks to [@katherinecodes](https://twitter.com/katherinecodes) for [readme.so](https://readme.so/), [@jessicaspacekat](https://twitter.com/jessicaspacekat) for [rikeripsum.com](http://rikeripsum.com), and [ansicolors](https://github.com/jonathaneunice/colors/).
## License

Tinta is licensed under both the [MIT License](LICENSE) and the [Hippocratic License](https://firstdonoharm.dev/version/2/1/license.html). Were a conflict or dispute to arise between these two licenses, the **Hippocratic License** license shall take precedence. Under its principles of Do No Harm, no portion of this software may be used to (or be a part of software that can be used to) cause, infer, encourage, incite, or otherwise lead to physical or verbal harm for any person or people, _especially_ marginalized and underrepresented people.

  
