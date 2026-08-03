import asyncio
import json
from typing import Callable

from pyscript import web, when

import jsonreflow

EXAMPLE_DATA = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [3.260, 50.82],
                        [3.83, 50.92],
                        [3.97, 51.24],
                        [3.55, 51.11],
                        [3.26, 50.82],
                    ]
                ],
            },
            "properties": {"color": "green"},
        }
    ],
}


def init():
    # Set version in footer
    for el in web.page.find(".jsonreflow-version"):
        el.innerText = jsonreflow.__version__

    # Load example JSON
    web.page["input-json"].value = json.dumps(EXAMPLE_DATA, indent=2)
    update_stats(text_id="input-json", stats_id="input-stats")
    do_reflow()


def do_reflow():
    input_json = web.page["input-json"].value
    indent = int(web.page["indent-select"].value)
    max_width = int(web.page["max-width-select"].value)

    try:
        data = json.loads(input_json)
        output_json = jsonreflow.dumps(data, indent=indent, max_width=max_width)
    except Exception as e:
        set_output_error(repr(e))
        return

    set_output_error(None)
    web.page["output-json"].value = output_json
    update_stats(text_id="output-json", stats_id="output-stats")


class Debouncer:
    """
    Delays calling a callback until `delay` seconds have passed
    since the last `trigger()` call.
    """

    def __init__(self, callback: Callable, delay: float = 0.4):
        self._delay = delay
        self._callback = callback
        self._task = None

    def trigger(self):
        if self._task is not None:
            self._task.cancel()
        self._task = asyncio.ensure_future(self._wait_and_call())

    async def _wait_and_call(self):
        await asyncio.sleep(self._delay)
        self._callback()


reflow_debouncer = Debouncer(do_reflow)


@when("input", "#input-json")
def input_changed(event):
    update_stats(text_id="input-json", stats_id="input-stats")
    reflow_debouncer.trigger()


@when("change", "#indent-select")
@when("change", "#max-width-select")
def option_changed(event):
    do_reflow()


def update_stats(text_id: str, stats_id: str) -> None:
    text = web.page[text_id].value
    lines = text.split("\n")
    longest_line = max((len(line) for line in lines), default=0)
    web.page[
        stats_id
    ].innerText = (
        f"({len(text)} chars, {len(lines)} lines, longest line: {longest_line} chars)"
    )


def set_output_error(message: str | None):
    output_error_element = web.page["output-error"]
    output_pane_element = web.page["output-pane"]

    if message:
        output_error_element.innerText = message
        output_pane_element.classes.add("error")
    else:
        output_error_element.innerText = ""
        output_pane_element.classes.remove("error")


init()
