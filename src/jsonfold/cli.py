import argparse
import json

from jsonfold.fold import MAX_WIDTH_DEFAULT, dumps, fold_iter


def main():
    cli = argparse.ArgumentParser(description="Fold JSON to fit within a given width")
    cli.add_argument(
        "input",
        nargs="?",
        type=argparse.FileType("r", encoding="utf-8"),
        default="-",
        help="Input JSON file (defaults to stdin)",
    )
    cli.add_argument(
        "--assume-formatted",
        action="store_true",
        help="""
            Assume the input is already properly formatted as multiline, indented JSON.
            Allows to fold without parsing the JSON, which is more efficient,
            and avoids subtle re-encoding issues.
        """,
    )
    cli.add_argument(
        "-w",
        "--max-width",
        type=int,
        default=MAX_WIDTH_DEFAULT,
        help=f"Maximum width for folded lines (default: {MAX_WIDTH_DEFAULT})",
    )

    args = cli.parse_args()
    if args.assume_formatted:
        for line in fold_iter(
            (s.rstrip() for s in args.input.readlines()), max_width=args.max_width
        ):
            print(line)
    else:
        data = json.load(args.input)
        # TODO: integrate with streaming JSON encoding
        print(dumps(data, max_width=args.max_width))


if __name__ == "__main__":
    main()
