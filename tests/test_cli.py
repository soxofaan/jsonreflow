import subprocess
import textwrap
from pathlib import Path
from typing import Iterable, Union

import pytest


def run_jsonreflow(
    args: Iterable[str] = (), stdin: Union[str, None] = None, check_success: bool = True
) -> subprocess.CompletedProcess:
    assert all(isinstance(arg, str) for arg in args)
    # Note: this assumes that the `jsonreflow` CLI is available in the PATH,
    # which should be the case in normal test setups.
    command = ["jsonreflow"] + list(args)
    result = subprocess.run(
        command,
        input=stdin,
        capture_output=True,
        text=True,
    )
    if check_success:
        result.check_returncode()
    return result


def test_help():
    result = run_jsonreflow(args=["--help"])
    assert "Reflow JSON to fit within a given line width" in result.stdout
    assert "--max-width" in result.stdout
    assert "--indent" in result.stdout
    assert "--assume-formatted" in result.stdout


def test_basic_stdin():
    result = run_jsonreflow(stdin='{"a":1, "b":[1,2,3]}')
    assert result.stdout == '{"a": 1, "b": [1, 2, 3]}\n'


def test_basic_file(tmp_path: Path):
    path = tmp_path / "data.json"
    path.write_text('{"a":1, "b":[1,2,3]}')
    result = run_jsonreflow(args=[str(path)])
    assert result.stdout == '{"a": 1, "b": [1, 2, 3]}\n'


@pytest.mark.parametrize(
    ["max_width", "expected"],
    [
        (80, '{"a": 123, "b": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}\n'),
        (40, '{\n  "a": 123,\n  "b": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]\n}\n'),
        (
            20,
            '{\n  "a": 123,\n  "b": [\n    0,\n    1,\n    2,\n    3,\n    4,\n    5,\n'
            "    6,\n    7,\n    8,\n    9\n  ]\n}\n",
        ),
    ],
)
def test_max_width(max_width, expected):
    stdin = '{"a":123, "b":[0,1,2,3,4,5,6,7,8,9]}'
    result = run_jsonreflow(stdin=stdin, args=["-w", str(max_width)])
    assert result.stdout == expected


@pytest.mark.parametrize(
    ["indent", "expected"],
    [
        (0, '{\n"a": 123,\n"b": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]\n}\n'),
        (1, '{\n "a": 123,\n "b": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]\n}\n'),
        (2, '{\n  "a": 123,\n  "b": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]\n}\n'),
        (
            8,
            '{\n        "a": 123,\n        "b": [\n                0,\n'
            "                1,\n                2,\n                3,\n"
            "                4,\n                5,\n                6,\n"
            "                7,\n                8,\n                9\n        ]\n}\n",
        ),
    ],
)
def test_indent(indent, expected):
    stdin = '{"a":123, "b":[0,1,2,3,4,5,6,7,8,9]}'
    result = run_jsonreflow(stdin=stdin, args=["-w", "40", "-i", str(indent)])
    assert result.stdout == expected


def test_invalid_json():
    stdin = "hello, not json"
    result = run_jsonreflow(stdin=stdin, check_success=False)
    assert result.returncode != 0
    # TODO: check for cleaner error message #4


@pytest.mark.parametrize(
    ["max_width", "expected"],
    [
        (80, '{"a": 123 + stuff, "b": [look ma, no quotes]}\n'),
        (40, '{\n  "a": 123 + stuff,\n  "b": [look ma, no quotes]\n}\n'),
    ],
)
def test_assume_formatted(max_width, expected):
    """
    In "assume-formatted" mode, the input is assumed to be properly formatted
    as multiline+indented JSON.
    It is also not parsed, so reflow should still work,
    even when the input is not valid JSON, as long as the indentation style is correct.
    """
    stdin = textwrap.dedent("""\
        {
          "a": 123 + stuff,
          "b": [
            look ma,
            no quotes
          ]
        }""")
    args = ["--assume-formatted", "-w", str(max_width)]
    result = run_jsonreflow(stdin=stdin, args=args)
    assert result.stdout == expected
