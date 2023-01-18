from typing import Any, Dict, Union

from flask_restx import Model, fields

from arbeitszeit_web.api_presenters.interfaces import (
    JsonDict,
    JsonString,
    JsonValue,
    Namespace,
)


class ModelWithSameNameExists(Exception):
    pass


def _register(schema: JsonDict, namespace: Namespace) -> Model:
    assert schema.schema_name
    model = {
        key: json_schema_to_flaskx(schema=value, namespace=namespace)
        for key, value in schema.members.items()
    }
    result = namespace.model(name=schema.schema_name, model=model)
    return result


def _register_as_nested(schema: JsonDict, namespace: Namespace) -> Model:
    assert schema.schema_name
    assert schema.as_list
    model = {
        key: fields.Nested(
            json_schema_to_flaskx(schema=value, namespace=namespace), as_list=True
        )
        for key, value in schema.members.items()
    }
    result = namespace.model(name=schema.schema_name, model=model)
    return result


def _prevent_overriding_of_model(schema: JsonDict, namespace: Namespace) -> None:
    """
    Ensure that a model previously registered on namespace does not get overridden.
    """
    assert schema.schema_name
    if schema.schema_name in namespace.models:
        raise ModelWithSameNameExists(
            f"Model with name {schema.schema_name} exists already."
        )


def json_schema_to_flaskx(
    schema: JsonValue, namespace: Namespace
) -> Union[Model, Dict[str, Any], type[fields.String]]:
    if isinstance(schema, JsonDict):
        if not schema.schema_name:
            result = {
                key: json_schema_to_flaskx(schema=value, namespace=namespace)
                for key, value in schema.members.items()
            }
            return result
        else:
            _prevent_overriding_of_model(schema, namespace)
            if schema.as_list:
                model = _register_as_nested(schema, namespace)
                return model
            else:
                model = _register(schema, namespace)
                return model
    else:
        assert isinstance(schema, JsonString)
        return fields.String