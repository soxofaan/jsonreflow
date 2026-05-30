
# JSON Reflow

Python library and CLI tool to reflow JSON files and streams,
to allow a better compromise between

- compactness:
  try to fit short arrays and objects on a single line,
  within a given line length limit
- human readability:
  indented JSON for larger constructs otherwise.



## The problem

Standard JSON serialization tools typically only provide two approaches:

- put everything on a single line:
  the most compact, but very poor for human readability

- spread out each and every array item and object property on its own line
  with appropriate indentation to visualize the structure.
  This is easier for humans to parse visually
  (which is why it is often referred to as "prettifying" or "beautifying"),
  but for larger documents, this easily becomes unwieldy, "too vertical"
  and very space-inefficient because of all the repeated indentation.


## Example

Consider the following example of a (Geo)JSON document.

### Compact

In compact form, you have one line, 83 characters in total, no whitespace:

```json
{"type":"Polygon","coordinates":[[[11.4,46.5],[10.3,55.3],[1.1,49.9],[11.4,46.5]]]}
```

### "Pretty"

In the so-called "pretty" form, using 2 space indentation (a common choice),
you have 23 lines, 233 characters, of which more than half are the spaces for indentation:

```json
{
  "type": "Polygon",
  "coordinates": [
    [
      [
        11.4,
        46.5
      ],
      [
        10.3,
        55.3
      ],
      [
        1.1,
        49.9
      ],
      [
        11.4,
        46.5
      ]
    ]
  ]
}
```


### JSON Reflow

JSON Reflow allows one to find a better compromise:
only serialize arrays or objects over multiple lines
if the single-line approach would exceed a given line length.

With the default settings (e.g. 80 characters line length limit, 2 spaces indentation),
JSON Reflow produces the following.
Just 4 lines, 99 characters in total, and only 4 spaces spent on indentation:

```json
{
  "type": "Polygon",
  "coordinates": [[[11.4, 46.5], [10.3, 55.3], [1.1, 49.9], [11.4, 46.5]]]
}
```

Taking a shorter line length limit of 40 characters causes a different reflow of the "coordinates" array,
resulting in 11 lines, 137 characters in total, and 38 spaces for indentation:

```json
{
  "type": "Polygon",
  "coordinates": [
    [
      [11.4, 46.5],
      [10.3, 55.3],
      [1.1, 49.9],
      [11.4, 46.5]
    ]
  ]
}
```



## Installation

### In a virtual environment

JSON reflow is a Python package and can be installed from PyPI using pip
(or something compatible like uv) into your Python environment:

```bash
pip install jsonreflow
```

### Standalone command line tool

If you're just interested in using the command line tool,
you probably want to install it in a more standalone way,
e.g. using [pipx](https://pipx.pypa.io/):

```bash
pipx install jsonreflow
```

Or [uv tool](https://docs.astral.sh/uv/concepts/tools/):

```bash
uv tool install jsonreflow
```

If your `PATH` is set up correctly according to the instructions of pipx or uv,
you should then be able to run the `jsonreflow` command, e.g.:

```bash
jsonreflow --help
```

### No-install usage

With [uvx (alias for `uv tool run`)](https://docs.astral.sh/uv/concepts/tools/),
you can also run the tool without (explicitly) installing it,

```bash
uvx jsonreflow --help
```


## Command line usage

The `jsonreflow` command line tool has built-in help
under the `--help` option:

```bash
jsonreflow --help
```

The most basic usage is just passing a JSON file path,
or reading from standard input if no file path is given:

```bash
# Provide a file path as argument,
jsonreflow data.json

# Or read from standard input
cat data.json | jsonreflow
```

This will reflow the JSON document with the default settings of
an 80 characters line length limit and 2 spaces indentation.

Line length limit and indentation can be customized:

```bash
jsonreflow --max-width 40 --indent 4 data.json
```

### "Assume formatted" mode

By default, JSON Reflow parses the input JSON en re-encodes it before reflowing,
to ensure that proper indentation is present for the reflowing logic to work correctly.
If you have data that is already properly JSON formatted with consistent indentation,
you can use the `--assume-formatted` option to skip the parsing and re-encoding step,
and directly reflow the input as-is.

This has some advantages:
- no effort is spent on parsing and re-encoding
- original data encoding and formatting is preserved:
  this avoids subtle data manipulation
  introduced by the parsing and re-encoding roundtrip
  (e.g. loss of decimal places in floats, or handling of unicode data)
- the document can be reflowed in a streaming fashion,
  line per line, without need to keep the entire document in memory.



## Design and implementation

- No required dependencies outside of the Python standard library
- The core reflow logic only manipulates whitespace,
  there is no requirement to parse the JSON and re-serialize it,
  which allows to preserve the original encoding
  and avoids subtle data manipulation that can be introduced by parsing and re-encoding
- The core reflow logic works in a streaming fashion
  (iterable input, generator output),
  so large JSON documents can be reflowed
  without loading the entire document into memory.


## References and related tools


Comparable tools:

- [lydell/json-stringify-pretty-compact](https://github.com/lydell/json-stringify-pretty-compact):
  JavaScript implementation.
  Provides an [online demo](https://lydell.github.io/json-stringify-pretty-compact/)
- [yairlenga/jsonfold](https://github.com/yairlenga/jsonfold)
  aims to have implementations in multiple languages (including Python and JavaScript).
  Fun fact: JSON Reflow was originally named "jsonfold",
  and while the initial implementation of JSON Reflow predates yairlenga/jsonfold (by just a couple of months)
  the latter was actually first published on PyPI,
  so I had to rename my package to "JSON Reflow".
