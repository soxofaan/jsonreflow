import contextlib
import json
import os
import tempfile
from pathlib import Path
from typing import Iterable, Iterator, List, Protocol, Union

MAX_WIDTH_DEFAULT = 80
INDENT_DEFAULT = 2


class SupportsRead(Protocol):
    def read(self, size: int = ..., /) -> str: ...
    def readlines(self) -> Iterable[str]: ...


class SupportsWrite(Protocol):
    def write(self, text: str, /) -> int: ...


def reflow_iter(
    lines: Iterable[str],
    *,
    max_width: int = MAX_WIDTH_DEFAULT,
) -> Iterator[str]:
    """
    Reflow an iterable of lines of JSON-encoded text to fit within a given line width.
    """
    # TODO: clarify that the given lines are expected to not have trailing newlines
    # TODO: be flexible/configurable about lines having newlines or not

    # Stack of buffers of possibly foldable levels.
    # Note that only the currently deepest levels are tracked,
    # levels more towards the top that are already collapsed
    # are not represented here anymore.
    buffer_stack: List[List[str]] = []

    for line in lines:
        stripped = line.strip()

        if stripped.endswith("{") or stripped.endswith("["):
            # Start a new level on the stack
            buffer_stack.append([])

        # Depending on whether we are at a possibly foldable level:
        # yield (collapse) or try folding
        if not buffer_stack:
            yield line
        else:
            buffer_stack[-1].append(line)

            if stripped in {"}", "},", "]", "],"}:
                # Close current level: time to see if we can fold to one-liner
                # or have to collapse to multi-line
                closed = buffer_stack.pop()
                folded = (
                    closed[0]
                    + " ".join(s.strip() for s in closed[1:-1])
                    + closed[-1].strip()
                )

                if len(folded) > max_width:
                    # Current level doesn't fit: collapse all levels we've been tracking
                    for level in buffer_stack:
                        yield from level
                    buffer_stack = []
                    yield from closed
                else:
                    # Move folded result up one level (unless it's collapsed already)
                    if buffer_stack:
                        buffer_stack[-1].append(folded)
                    else:
                        yield folded


def reflow(encoded: str, *, max_width: int = MAX_WIDTH_DEFAULT) -> str:
    """
    Reflow the given encoded JSON string.
    """
    return "\n".join(
        reflow_iter(
            lines=encoded.split("\n"),
            max_width=max_width,
        )
    )


def dumps(
    obj,
    *,
    max_width: int = MAX_WIDTH_DEFAULT,
    indent: int = INDENT_DEFAULT,
) -> str:
    """
    Serialize `obj` to a JSON-formatted string,
    like `json.dumps` from the standard library,
    but with reflowing to fit within a given line width.
    """
    # TODO: support all/most of the original json.dumps arguments?
    return reflow(
        encoded=json.dumps(obj=obj, indent=indent),
        max_width=max_width,
    )


def _chunks_to_lines(chunks: Iterable[str]) -> Iterator[str]:
    """
    Convert an iterable of JSON-encoded chunks
    into an iterator of lines (without trailing newlines).
    """
    buffer = ""
    for chunk in chunks:
        parts = chunk.split("\n")
        for part in parts[:-1]:
            yield buffer + part
            buffer = ""
        buffer += parts[-1]

    if buffer:
        yield buffer


def _json_encode_lines(obj, indent: int = INDENT_DEFAULT) -> Iterator[str]:
    """
    Use stdlib json.JSONEncoder to JSON-encode given object
    and produce line per line
    """
    # TODO: support all/most of JSONEncoder's arguments?
    encoder = json.JSONEncoder(indent=indent)
    chunks = encoder.iterencode(obj)
    yield from _chunks_to_lines(chunks)


def dump(
    obj,
    fp,
    *,
    max_width: int = MAX_WIDTH_DEFAULT,
    indent: int = INDENT_DEFAULT,
) -> None:
    """
    Serialize `obj` as a JSON-formatted stream to `fp`
    (a `.write()`-supporting file-like object),
    like `json.dump` from the standard library,
    but with reflowing to fit within a given line width.
    """
    # TODO: support all/most of JSONEncoder's arguments?
    encoded_lines = _json_encode_lines(obj=obj, indent=indent)
    for line in reflow_iter(lines=encoded_lines, max_width=max_width):
        # TODO: classic json.dump() does not add newline after last line
        fp.write(line + "\n")


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


def reflow_file(
    input: Union[str, Path, SupportsRead],
    output: Union[str, Path, SupportsWrite, None],
    *,
    assume_formatted: bool = False,
    max_width: int = MAX_WIDTH_DEFAULT,
    indent: int = INDENT_DEFAULT,
) -> None:
    """
    Reflow JSON from the given file and write back in-place
    or write to another file.
    """
    if isinstance(input, (str, Path)):
        input_context = Path(input).open(mode="r", encoding="utf-8")  # noqa: SIM115
    else:
        # Assume it's already a readable file-like object
        input_context = contextlib.nullcontext(input)

    if output is None:
        # In-place mode
        assert isinstance(input, (str, Path))
        output_context = _temp_sink_and_rename_on_exit(path=Path(input))
    elif isinstance(output, (str, Path)):
        output_context = _temp_sink_and_rename_on_exit(path=Path(output))
    else:
        # Assume it's already a writable file-like object
        output_context = contextlib.nullcontext(output)

    with output_context as output_file, input_context as input_file:
        if assume_formatted:
            encoded_lines = (s.rstrip() for s in input_file.readlines())
        else:
            data = json.load(fp=input_file)
            encoded_lines = _json_encode_lines(obj=data, indent=indent)

        for line in reflow_iter(lines=encoded_lines, max_width=max_width):
            output_file.write(line + "\n")
