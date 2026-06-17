import argparse
import sys
from pathlib import Path

from jsonreflow.reflow import INDENT_DEFAULT, MAX_WIDTH_DEFAULT, reflow_file

_STDIN_NAME = "-"


def main():
    cli = argparse.ArgumentParser(
        description="Reflow JSON to fit within a given line width"
    )
    cli.add_argument(
        "input",
        nargs="?",
        type=str,
        default=_STDIN_NAME,
        help="Input JSON file (defaults to stdin)",
    )
    cli.add_argument(
        "--assume-formatted",
        action="store_true",
        help="""
            Assume the input is already properly formatted as multiline, indented JSON.
            Allows to reflow without parsing the JSON, which is more efficient,
            and avoids subtle re-encoding issues.
        """,
    )
    cli.add_argument(
        "-w",
        "--max-width",
        type=int,
        default=MAX_WIDTH_DEFAULT,
        help=f"Maximum line width to reflow for (default: {MAX_WIDTH_DEFAULT})",
    )
    cli.add_argument(
        "-i",
        "--indent",
        type=int,
        default=INDENT_DEFAULT,
        help=f"""
            Number of spaces to use for indentation (default: {INDENT_DEFAULT}).
            Note: this is only applied when jsonreflow re-JSON-encodes the data,
            e.g. not when using --assume-formatted.
            """,
    )
    cli.add_argument(
        "--inplace",
        action="store_true",
        help="""
            Reflow the given input file in-place,
            instead of printing to standard output.
        """,
    )

    args = cli.parse_args()

    # Handle input source
    if args.input == _STDIN_NAME:
        source = sys.stdin
    else:
        source = Path(args.input)
        if not source.is_file():
            # TODO: cleaner CLI error reporting than raw exception
            raise ValueError(f"Input path {source} is not a valid file")

    # Handle output destination
    if args.inplace:
        if args.input == _STDIN_NAME:
            raise ValueError("In-place modifying standard input does not make sense.")
        sink = Path(args.input)
    else:
        sink = sys.stdout

    reflow_file(
        source=source,
        sink=sink,
        assume_formatted=args.assume_formatted,
        max_width=args.max_width,
        indent=args.indent,
    )


if __name__ == "__main__":
    main()
