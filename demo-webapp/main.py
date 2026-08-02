import json

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

for el in web.page.find(".jsonreflow-version"):
    el.innerText = jsonreflow.__version__


web.page["input-json"].value = json.dumps(EXAMPLE_DATA, indent=2)
web.page["output-json"].value = jsonreflow.dumps(EXAMPLE_DATA, indent=2)


@when("click", "#reflow-button")
def reflow(event):
    input_json = web.page["input-json"].value
    indent = int(web.page["indent-select"].value)
    max_width = int(web.page["max-width-select"].value)

    # output_json = jsonreflow.reflow(input_json)
    data = json.loads(input_json)
    output_json = jsonreflow.dumps(data, indent=indent, max_width=max_width)

    web.page["output-json"].value = output_json
