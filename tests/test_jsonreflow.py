import json
import textwrap
from typing import Iterable, List

import pytest

from jsonreflow import dumps, reflow_iter


def test_dumps_none():
    assert dumps(None) == "null"


def test_dumps_int():
    assert dumps(123) == "123"
    assert dumps(-123) == "-123"


def test_dumps_float():
    assert dumps(123.5) == "123.5"


def test_dumps_bool():
    assert dumps(True) == "true"
    assert dumps(False) == "false"


def test_dumps_string():
    assert dumps("hello world") == '"hello world"'


def test_dumps_empty_list():
    assert dumps([]) == "[]"
    assert dumps(()) == "[]"


def test_dumps_empty_dict():
    assert dumps({}) == "{}"


def test_dumps_flat_list():
    assert dumps([1, 2, 3, 4, 5]) == "[1, 2, 3, 4, 5]"
    assert dumps([1, 2, 3, 4, 5], max_width=10) == "[\n  1,\n  2,\n  3,\n  4,\n  5\n]"
    assert dumps([1, 2, 3, 4, 5], max_width=1) == "[\n  1,\n  2,\n  3,\n  4,\n  5\n]"


def test_dumps_flat_dict():
    assert (
        dumps({"name": "alice", "color": "green"})
        == '{"name": "alice", "color": "green"}'
    )
    assert (
        dumps({"name": "alice", "color": "green"}, max_width=10)
        == '{\n  "name": "alice",\n  "color": "green"\n}'
    )
    assert (
        dumps({"name": "alice", "color": "green"}, max_width=1)
        == '{\n  "name": "alice",\n  "color": "green"\n}'
    )


@pytest.mark.parametrize(
    ["max_width", "obj", "expected"],
    [
        (
            80,
            {"five": list(range(5)), "ten": list(range(10))},
            '{"five": [0, 1, 2, 3, 4], "ten": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}',
        ),
        (
            40,
            {"five": list(range(5)), "ten": list(range(10))},
            """\
            {
              "five": [0, 1, 2, 3, 4],
              "ten": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            }""",
        ),
        (
            30,
            {"five": list(range(5)), "ten": list(range(10))},
            """\
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
            }""",
        ),
        (
            80,
            {str(x): chr(97 + x) * x for x in range(5)},
            '{"0": "", "1": "b", "2": "cc", "3": "ddd", "4": "eeee"}',
        ),
        (
            40,
            {str(x): chr(97 + x) * x for x in range(5)},
            """\
            {
              "0": "",
              "1": "b",
              "2": "cc",
              "3": "ddd",
              "4": "eeee"
            }""",
        ),
    ],
)
def test_dumps_listings(max_width, obj, expected):
    expected = textwrap.dedent(expected)
    assert dumps(obj, max_width=max_width) == expected


@pytest.mark.parametrize(
    ["max_width", "obj", "expected"],
    [
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
            """\
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
            }""",
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
            """\
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
            }""",  # noqa: E501
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
            """\
            {
              "a": {
                "bb": {
                  "ccc": {"dddd": {"eeeee": {"ffffff": "foo"}}},
                  "CCC": {"D": 13, "DD": 133, "DDD": 1333}
                }
              }
            }""",
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
            """\
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
            }""",
        ),
    ],
)
def test_dumps_deep_nesting(obj, max_width, expected):
    expected = textwrap.dedent(expected)
    assert dumps(obj, max_width=max_width) == expected


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
