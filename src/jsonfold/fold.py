import json
from typing import Iterable, Iterator, List

MAX_WIDTH_DEFAULT = 80


def fold_iter(
    lines: Iterable[str], max_width: int = MAX_WIDTH_DEFAULT
) -> Iterator[str]:
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


def fold(encoded: str, max_width: int = MAX_WIDTH_DEFAULT) -> str:
    return "\n".join(fold_iter(encoded.split("\n"), max_width=max_width))


def dumps(obj, max_width: int = MAX_WIDTH_DEFAULT) -> str:
    return fold(json.dumps(obj=obj, indent=2), max_width=max_width)
