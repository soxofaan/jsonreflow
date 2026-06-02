import argparse
import contextlib
import json
import os
import sys
import tempfile
from pathlib import Path

import jsonreflow
from jsonreflow.reflow import INDENT_DEFAULT, MAX_WIDTH_DEFAULT

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
        input_context = contextlib.nullcontext(sys.stdin)
    else:
        input_path = Path(args.input)
        if not input_path.is_file():
            # TODO: cleaner CLI error reporting than raw exception
            raise ValueError(f"Input path {input_path} is not a file")
        input_context = input_path.open(mode="r", encoding="utf-8")

    # Handle output destination
    if args.inplace:
        if args.input == _STDIN_NAME:
            raise ValueError("In-place modifying standard input does not make sense.")
        output_context = _temp_sink_and_rename_on_exit(path=Path(args.input))
    else:
        output_context = contextlib.nullcontext(sys.stdout)

    with output_context as output_file, input_context as input_file:
        if args.assume_formatted:
            for line in jsonreflow.reflow_iter(
                lines=(s.rstrip() for s in input_file.readlines()),
                max_width=args.max_width,
            ):
                output_file.write(line + "\n")
        else:
            data = json.load(fp=input_file)
            jsonreflow.dump(
                obj=data, fp=output_file, max_width=args.max_width, indent=args.indent
            )


@contextlib.contextmanager
def _temp_sink_and_rename_on_exit(
    path: Path, *, mode: str = "w", encoding: str = "utf-8"
):
    """
    Context manager for safe in-place writing of a file
    (avoid truncating the original file too early):
    use a temporary file during writing,
    and atomically replace the target path on successful exit of the context manager.
    """

    # Use temp file in same directory (file system) to allow atomic move
    folder = path.parent

    with tempfile.NamedTemporaryFile(
        mode=mode,
        encoding=encoding,
        prefix=".jsonreflow_tmp_",
        dir=folder,
        delete=False,
    ) as temp_file:
        try:
            yield temp_file
            temp_file.flush()
            temp_file.close()
            # Rename to target path (should be atomic move)
            os.replace(src=temp_file.name, dst=path)
        except Exception:
            # Clean up temp file on error
            with contextlib.suppress(FileNotFoundError):
                os.remove(temp_file.name)
            raise


if __name__ == "__main__":
    main()
