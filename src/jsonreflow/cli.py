import argparse
import json

from jsonreflow.reflow import INDENT_DEFAULT, MAX_WIDTH_DEFAULT, dumps, reflow_iter


def main():
    cli = argparse.ArgumentParser(
        description="Reflow JSON to fit within a given line width"
    )
    cli.add_argument(
        "input",
        nargs="?",
        # TODO: argparse.FileType is deprecated since Python 3.14
        type=argparse.FileType("r", encoding="utf-8"),
        default="-",
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

    args = cli.parse_args()
    if args.assume_formatted:
        for line in reflow_iter(
            (s.rstrip() for s in args.input.readlines()), max_width=args.max_width
        ):
            print(line)
    else:
        data = json.load(args.input)
        # TODO: integrate with streaming JSON encoding
        print(dumps(data, max_width=args.max_width, indent=args.indent))


if __name__ == "__main__":
    main()
