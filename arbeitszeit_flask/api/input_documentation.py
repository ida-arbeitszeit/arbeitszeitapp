from typing import Any, Callable, Dict, Sequence, Union

from flask_restx import Namespace

from arbeitszeit_web.api.controllers.parameters import (
    BodyParameter,
    PathParameter,
    QueryParameter,
)

Parameter = Union[QueryParameter, BodyParameter, PathParameter]
TypeLookupTable = Dict[type, str]

type_lookup_table: TypeLookupTable = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
}


class with_input_documentation:
    def __init__(
        self,
        expected_inputs: Sequence[Parameter],
        namespace: Namespace,
    ) -> None:
        self._expected_inputs = expected_inputs
        self._namespace = namespace

    def __call__(self, func: Callable) -> Callable:
        """See https://swagger.io/specification/v2 for more information on the OpenAPI specification."""
        params: Dict[str, Any] = {}
        for expected_input in self._expected_inputs:
            if isinstance(expected_input, PathParameter):
                self._add_path_parameter(params, expected_input)
            elif isinstance(expected_input, QueryParameter):
                self._add_query_parameter(params, expected_input)
            else:
                assert isinstance(expected_input, BodyParameter)
                self._add_body_parameter(params, expected_input)
        decorator = self._namespace.doc(params=params)
        decorator(func)
        return func

    def _add_path_parameter(self, params: Dict[str, Any], param: PathParameter) -> None:
        params[param.name] = {
            "description": param.description,
            "type": "string",
            "required": True,
            "in": "path",
        }

    def _add_query_parameter(
        self, params: Dict[str, Any], param: QueryParameter
    ) -> None:
        params[param.name] = {
            "description": param.description,
            "type": type_lookup_table[param.type],
            "default": param.default,
            "required": param.required,
            "in": "query",
        }

    def _add_body_parameter(self, params: Dict[str, Any], param: BodyParameter) -> None:
        if "payload" not in params:
            params["payload"] = {
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {param.name: {"type": type_lookup_table[param.type]}},
                },
            }
        else:
            params["payload"]["schema"]["properties"][param.name] = {
                "type": type_lookup_table[param.type]
            }
