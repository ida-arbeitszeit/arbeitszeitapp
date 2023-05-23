from typing import List

from flask_restx.reqparse import RequestParser

from arbeitszeit_web.api_controllers.query_plans_api_controller import ExpectedInput


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
            location=input.location,
        )
    return parser
