import json

from pyscript import web, when

import jsonreflow


@when("click", "#reflow-button")
def reflow(event):
    input_json = web.page["input-json"].value

    # output_json = jsonreflow.reflow(input_json)
    data = json.loads(input_json)
    output_json = jsonreflow.dumps(data, indent=2)

    web.page["output-json"].value = output_json
