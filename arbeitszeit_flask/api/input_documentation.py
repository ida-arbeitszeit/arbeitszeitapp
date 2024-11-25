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
        for input_ in self._expected_inputs:
            match input_:
                case PathParameter():
                    params[input_.name] = {
                        "description": input_.description,
                        "type": "string",
                        "required": True,
                        "in": "path",
                    }
                case QueryParameter():
                    params[input_.name] = {
                        "description": input_.description,
                        "type": type_lookup_table[input_.type],
                        "default": input_.default,
                        "required": input_.required,
                        "in": "query",
                    }
                case BodyParameter():
                    if "payload" not in params:
                        params["payload"] = {
                            "in": "body",
                            "required": True,
                            "schema": {
                                "type": "object",
                                "properties": {
                                    input_.name: {
                                        "type": type_lookup_table[input_.type]
                                    }
                                },
                            },
                        }
                    else:
                        params["payload"]["schema"]["properties"][input_.name] = {
                            "type": type_lookup_table[input_.type]
                        }
                case _:
                    raise ValueError(f"Unexpected parameter type: {type(input_)}")
        decorator = self._namespace.doc(params=params)
        decorator(func)
        return func
