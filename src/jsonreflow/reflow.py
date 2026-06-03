import json
from typing import Iterable, Iterator, List

MAX_WIDTH_DEFAULT = 80
INDENT_DEFAULT = 2


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
    encoder = json.JSONEncoder(indent=indent)
    chunks = encoder.iterencode(obj)
    lines = reflow_iter(lines=_chunks_to_lines(chunks), max_width=max_width)
    for line in lines:
        # TODO: classic json.dump() does not add newline after last line
        fp.write(line + "\n")
