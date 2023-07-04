from typing import List

from flask_restx.reqparse import RequestParser

from arbeitszeit_web.api.controllers.expected_input import InputLocation
from arbeitszeit_web.api.controllers.query_plans_api_controller import ExpectedInput


def _generate_location(location: InputLocation) -> str:
    if location == InputLocation.query:
        return "query"
    elif location == InputLocation.form:
        return "form"
    else:
        return "path"


def generate_input_documentation(
    expected_inputs: List[ExpectedInput],
) -> RequestParser:
    parser = RequestParser()
    for input in expected_inputs:
        parser.add_argument(
            name=input.name,
            type=input.type,
            help=input.description,
            default=input.default,
            location=_generate_location(input.location),
            required=input.required,
        )
    return parser
