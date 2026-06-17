import json
import textwrap
from io import StringIO
from pathlib import Path
from typing import Iterable, List

import pytest

from jsonreflow import dump, dumps, reflow_iter
from jsonreflow.reflow import reflow_file

# Simple cases (obj, expected) of scalar values or small structures
DUMP_CASES_SIMPLE = [
    (None, "null"),
    (123, "123"),
    (-123, "-123"),
    (123.45, "123.45"),
    (1e6, "1000000.0"),
    (1e-3, "0.001"),
    (1e-6, "1e-06"),
    (True, "true"),
    (False, "false"),
    ("hello dump", '"hello dump"'),
    ([], "[]"),
    ([[]], "[[]]"),
    ([1, 2, 3], "[1, 2, 3]"),
    ((), "[]"),
    (((),), "[[]]"),
    ((1, "two"), '[1, "two"]'),
    ({}, "{}"),
    ({1: "one", "two": 2}, '{"1": "one", "two": 2}'),
]


@pytest.mark.parametrize(
    ["obj", "expected"],
    DUMP_CASES_SIMPLE,
)
def test_dumps_basic(obj, expected):
    assert dumps(obj) == expected


@pytest.mark.parametrize(
    ["obj", "expected"],
    DUMP_CASES_SIMPLE,
)
def test_dump_basic(tmp_path, obj, expected):
    path = tmp_path / "result.json"
    with path.open("w") as f:
        dump(obj, f)
    assert path.read_text() == expected + "\n"


# Cases (max_width, obj, expected) of basic flat structures
DUMP_CASES_FLAT_STRUCTURE = [
    (
        100,
        [1, 2, 3, 4, 5],
        "[1, 2, 3, 4, 5]",
    ),
    (
        10,
        [1, 2, 3, 4, 5],
        "[\n  1,\n  2,\n  3,\n  4,\n  5\n]",
    ),
    (
        1,
        [1, 2, 3, 4, 5],
        "[\n  1,\n  2,\n  3,\n  4,\n  5\n]",
    ),
    (
        100,
        {"name": "alice", "color": "green"},
        '{"name": "alice", "color": "green"}',
    ),
    (
        10,
        {"name": "alice", "color": "green"},
        '{\n  "name": "alice",\n  "color": "green"\n}',
    ),
    (
        1,
        {"name": "alice", "color": "green"},
        '{\n  "name": "alice",\n  "color": "green"\n}',
    ),
]


@pytest.mark.parametrize(
    ["max_width", "obj", "expected"],
    DUMP_CASES_FLAT_STRUCTURE,
)
def test_dumps_flat_structure(max_width, obj, expected):
    assert dumps(obj, max_width=max_width) == expected


@pytest.mark.parametrize(
    ["max_width", "obj", "expected"],
    DUMP_CASES_FLAT_STRUCTURE,
)
def test_dump_flat_structure(tmp_path, max_width, obj, expected):
    path = tmp_path / "result.json"
    with path.open("w") as f:
        dump(obj, f, max_width=max_width)
    assert path.read_text() == expected + "\n"


# Cases (max_width, obj, expected) of nested structures
DUMP_CASES_NESTED = [
    (
        80,
        {"five": list(range(5)), "ten": list(range(10))},
        '{"five": [0, 1, 2, 3, 4], "ten": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}',
    ),
    (
        40,
        {"five": list(range(5)), "ten": list(range(10))},
        textwrap.dedent("""\
            {
              "five": [0, 1, 2, 3, 4],
              "ten": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            }"""),
    ),
    (
        30,
        {"five": list(range(5)), "ten": list(range(10))},
        textwrap.dedent("""\
            {
              "five": [0, 1, 2, 3, 4],
              "ten": [
                0,
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9
              ]
            }"""),
    ),
    (
        80,
        {str(x): chr(97 + x) * x for x in range(5)},
        '{"0": "", "1": "b", "2": "cc", "3": "ddd", "4": "eeee"}',
    ),
    (
        40,
        {str(x): chr(97 + x) * x for x in range(5)},
        textwrap.dedent("""\
            {
              "0": "",
              "1": "b",
              "2": "cc",
              "3": "ddd",
              "4": "eeee"
            }"""),
    ),
    (
        80,
        {
            "query": "get stuff",
            "results": {
                "count": 5,
                "data": [
                    {"id": 1, "name": "Alice", "payments": None},
                    {"id": 23, "name": "Bob", "payments": [100, 200]},
                    {
                        "id": 3000,
                        "name": "Carol",
                        "status": "premium",
                        "payments": [1000, 3000, 2000, 2, -5],
                    },
                    {"id": 44, "name": "Dave", "payments": [1, 5]},
                    {
                        "id": 555,
                        "name": "Eric",
                        "payments": [44, {"price": 666, "currency": "tulip bulbs"}],
                    },
                ],
            },
            "_id": "123kthxbye",
        },
        textwrap.dedent("""\
            {
              "query": "get stuff",
              "results": {
                "count": 5,
                "data": [
                  {"id": 1, "name": "Alice", "payments": null},
                  {"id": 23, "name": "Bob", "payments": [100, 200]},
                  {
                    "id": 3000,
                    "name": "Carol",
                    "status": "premium",
                    "payments": [1000, 3000, 2000, 2, -5]
                  },
                  {"id": 44, "name": "Dave", "payments": [1, 5]},
                  {
                    "id": 555,
                    "name": "Eric",
                    "payments": [44, {"price": 666, "currency": "tulip bulbs"}]
                  }
                ]
              },
              "_id": "123kthxbye"
            }"""),
    ),
    (
        120,
        {
            "query": "get stuff",
            "results": {
                "count": 5,
                "data": [
                    {"id": 1, "name": "Alice", "payments": None},
                    {"id": 23, "name": "Bob", "payments": [100, 200]},
                    {
                        "id": 3000,
                        "name": "Carol",
                        "status": "premium",
                        "payments": [1000, 3000, 2000, 2, -5],
                    },
                    {"id": 44, "name": "Dave", "payments": [1, 5]},
                    {
                        "id": 555,
                        "name": "Eric",
                        "payments": [44, {"price": 666, "currency": "tulip bulbs"}],
                    },
                ],
            },
            "_id": "123kthxbye",
        },
        textwrap.dedent("""\
            {
              "query": "get stuff",
              "results": {
                "count": 5,
                "data": [
                  {"id": 1, "name": "Alice", "payments": null},
                  {"id": 23, "name": "Bob", "payments": [100, 200]},
                  {"id": 3000, "name": "Carol", "status": "premium", "payments": [1000, 3000, 2000, 2, -5]},
                  {"id": 44, "name": "Dave", "payments": [1, 5]},
                  {"id": 555, "name": "Eric", "payments": [44, {"price": 666, "currency": "tulip bulbs"}]}
                ]
              },
              "_id": "123kthxbye"
            }"""),  # noqa: E501
    ),
    (
        80,
        {
            "a": {
                "bb": {
                    "ccc": {
                        "dddd": {
                            "eeeee": {
                                "ffffff": "foo",
                            },
                        }
                    },
                    "CCC": {
                        "D": 13,
                        "DD": 133,
                        "DDD": 1333,
                    },
                }
            }
        },
        textwrap.dedent("""\
            {
              "a": {
                "bb": {
                  "ccc": {"dddd": {"eeeee": {"ffffff": "foo"}}},
                  "CCC": {"D": 13, "DD": 133, "DDD": 1333}
                }
              }
            }"""),
    ),
    (
        120,
        {
            "a": {
                "bb": {
                    "ccc": {
                        "dddd": {
                            "eeeee": {
                                "ffffff": "foo",
                            },
                        }
                    },
                    "CCC": {
                        "D": 13,
                        "DD": 133,
                        "DDD": 1333,
                    },
                }
            }
        },
        '{"a": {"bb": {"ccc": {"dddd": {"eeeee": {"ffffff": "foo"}}}, "CCC": {"D": 13, "DD": 133, "DDD": 1333}}}}',  # noqa: E501
    ),
    (
        40,
        {
            "a": {
                "bb": {
                    "ccc": {
                        "dddd": {
                            "eeeee": {
                                "ffffff": "foo",
                            },
                        }
                    },
                    "CCC": {
                        "D": 13,
                        "DD": 133,
                        "DDD": 1333,
                    },
                }
            }
        },
        textwrap.dedent("""\
            {
              "a": {
                "bb": {
                  "ccc": {
                    "dddd": {
                      "eeeee": {"ffffff": "foo"}
                    }
                  },
                  "CCC": {
                    "D": 13,
                    "DD": 133,
                    "DDD": 1333
                  }
                }
              }
            }"""),
    ),
]


@pytest.mark.parametrize(
    ["max_width", "obj", "expected"],
    DUMP_CASES_NESTED,
)
def test_dumps_nested(max_width, obj, expected):
    assert dumps(obj, max_width=max_width) == expected


@pytest.mark.parametrize(
    ["max_width", "obj", "expected"],
    DUMP_CASES_NESTED,
)
def test_dump_nested(tmp_path, max_width, obj, expected):
    path = tmp_path / "result.json"
    with path.open("w") as f:
        dump(obj, f, max_width=max_width)
    assert path.read_text() == expected + "\n"


class TrackingIterator:
    """
    Wrapper for an iterable of strings, to keep track of what has been consumed already.
    """

    def __init__(self, items: Iterable[str]):
        self._items = iter(items)
        self.consumed = []
        self._report_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        item = next(self._items)
        self.consumed.append(item)
        return item

    def new_consumed(self) -> List[str]:
        """Report newly consumed items since the last call."""
        index = self._report_index
        self._report_index = len(self.consumed)
        return self.consumed[index:]


def test_tracking_iterator_basic():
    iterator = TrackingIterator(["a", "b", "c"])

    assert iterator.consumed == []
    assert iterator.new_consumed() == []

    assert next(iterator) == "a"
    assert iterator.consumed == ["a"]
    assert iterator.new_consumed() == ["a"]

    assert next(iterator) == "b"
    assert iterator.consumed == ["a", "b"]

    assert next(iterator) == "c"
    assert iterator.consumed == ["a", "b", "c"]
    assert iterator.new_consumed() == ["b", "c"]
    assert iterator.new_consumed() == []

    with pytest.raises(StopIteration):
        next(iterator)
    assert iterator.consumed == ["a", "b", "c"]
    assert iterator.new_consumed() == []


def test_reflow_iter_flushing_simple_one_line():
    """
    Trivial case: everything fits on one line,
    so we should consume all input lines immediately.
    """
    data = {"color": "green", "shape": "square"}
    input_lines = TrackingIterator(json.dumps(data, indent=2).split("\n"))

    folded = reflow_iter(input_lines, max_width=80)
    assert input_lines.consumed == []

    line = next(folded)
    assert line == '{"color": "green", "shape": "square"}'
    assert input_lines.consumed == [
        "{",
        '  "color": "green",',
        '  "shape": "square"',
        "}",
    ]


def test_reflow_iter_flushing_simple_multiline():
    """
    Multi-line result, but just one level,
    so all lines should be consumed immediately.
    """
    data = {"color": "green", "shape": "square"}
    input_lines = TrackingIterator(json.dumps(data, indent=2).split("\n"))

    folded = reflow_iter(input_lines, max_width=20)
    assert input_lines.new_consumed() == []

    assert next(folded) == "{"
    assert input_lines.new_consumed() == [
        "{",
        '  "color": "green",',
        '  "shape": "square"',
        "}",
    ]

    assert next(folded) == '  "color": "green",'
    assert input_lines.new_consumed() == []

    assert next(folded) == '  "shape": "square"'
    assert input_lines.new_consumed() == []

    assert next(folded) == "}"
    assert input_lines.new_consumed() == []

    with pytest.raises(StopIteration):
        _ = next(folded)


def test_reflow_iter_flushing_nested():
    """Multi-line result with nesting: input is consumed in chunks."""
    data = {"three": list(range(3)), "five": list(range(5)), "ten": list(range(10))}
    input_lines = TrackingIterator(json.dumps(data, indent=2).split("\n"))

    folded = reflow_iter(input_lines, max_width=25)
    assert input_lines.new_consumed() == []

    # Top level flush: while "three" would fit on one line, "five" would overflow.
    assert next(folded) == "{"
    assert input_lines.new_consumed() == [
        "{",
        '  "three": [',
        "    0,",
        "    1,",
        "    2",
        "  ],",
        # TODO: with the next line, it should already be possible to determine
        #       that "five" won't fit, and it's already time to flush
        #       without further consumption.
        '  "five": [',
        "    0,",
        "    1,",
        "    2,",
        "    3,",
        "    4",
        "  ],",
    ]

    # "three" fits on one line
    assert next(folded) == '  "three": [0, 1, 2],'
    assert input_lines.new_consumed() == []

    # "five" doesn't fit, so we get multiple lines
    assert next(folded) == '  "five": ['
    assert input_lines.new_consumed() == []

    for x in range(4):
        assert next(folded) == f"    {x},"
        assert input_lines.new_consumed() == []

    assert next(folded) == "    4"
    assert input_lines.new_consumed() == []

    assert next(folded) == "  ],"
    assert input_lines.new_consumed() == []

    # Time for "ten": also doesn't fit. Buffer is empty at this point,
    # so we have to consume a bit too.
    assert next(folded) == '  "ten": ['
    assert input_lines.new_consumed() == [
        '  "ten": [',
        "    0,",
        "    1,",
        "    2,",
        "    3,",
        "    4,",
        "    5,",
        "    6,",
        "    7,",
        "    8,",
        "    9",
        "  ]",
    ]

    for x in range(9):
        assert next(folded) == f"    {x},"
        assert input_lines.new_consumed() == []

    assert next(folded) == "    9"
    assert input_lines.new_consumed() == []

    assert next(folded) == "  ]"
    assert input_lines.new_consumed() == []

    # Final closing brace
    assert next(folded) == "}"
    assert input_lines.new_consumed() == [
        "}",
    ]

    with pytest.raises(StopIteration):
        _ = next(folded)
    assert input_lines.new_consumed() == []


@pytest.mark.parametrize(
    ["max_width", "obj", "expected"],
    DUMP_CASES_NESTED,
)
@pytest.mark.parametrize(
    ["input_path_type", "output_path_type"],
    [
        (str, str),
        (str, Path),
        (Path, str),
        (Path, Path),
    ],
)
def test_reflow_file_with_paths(
    tmp_path, input_path_type, output_path_type, max_width, obj, expected
):
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "output.json"
    input_path.write_text(json.dumps(obj, indent=2))

    reflow_file(
        input=input_path_type(input_path),
        output=output_path_type(output_path),
        max_width=max_width,
        indent=2,
    )

    assert output_path.read_text() == expected + "\n"


@pytest.mark.parametrize(
    ["max_width", "obj", "expected"],
    DUMP_CASES_NESTED,
)
@pytest.mark.parametrize(
    ["input_path_type", "output_path_type"],
    [
        (str, str),
        (str, Path),
        (str, None),
        (Path, str),
        (Path, Path),
        (Path, None),
    ],
)
def test_reflow_file_with_paths_and_inplace_mode(
    tmp_path, input_path_type, output_path_type, max_width, obj, expected
):
    path = tmp_path / "data.json"
    path.write_text(json.dumps(obj, indent=2))
    reflow_file(
        input=input_path_type(path),
        output=(
            # Implicit or explicit in-place output?
            output_path_type(path) if output_path_type is not None else None
        ),
        max_width=max_width,
        indent=2,
    )
    assert path.read_text() == expected + "\n"


@pytest.mark.parametrize(
    ["max_width", "obj", "expected"],
    DUMP_CASES_NESTED,
)
def test_reflow_file_with_stringio(max_width, obj, expected):
    input = StringIO(json.dumps(obj, indent=2))
    output = StringIO()
    reflow_file(
        input=input,
        output=output,
        max_width=max_width,
        indent=2,
    )
    assert output.getvalue() == expected + "\n"
