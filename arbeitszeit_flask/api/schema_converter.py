from typing import Any, Dict, Union

from flask_restx import Model, fields

from arbeitszeit_web.api_presenters.interfaces import (
    JsonBoolean,
    JsonDatetime,
    JsonDecimal,
    JsonDict,
    JsonString,
    JsonValue,
    Namespace,
)


class ModelWithSameNameExists(Exception):
    pass


def _prevent_overriding(schema_name: str, namespace: Namespace) -> None:
    """
    Ensure that a model previously registered on namespace does not get overridden.
    """
    assert schema_name
    if schema_name in namespace.models:
        raise ModelWithSameNameExists(f"Model with name {schema_name} exists already.")


def _register_model_for_documentation(
    schema_name: str, namespace: Namespace, model: Dict[str, Any]
):
    assert schema_name
    _prevent_overriding(schema_name, namespace)
    registered_model = namespace.model(name=schema_name, model=model)
    return registered_model


def _convert_json_dict(
    schema: JsonDict, namespace: Namespace
) -> Union[Dict[str, Any], Model]:
    model: Dict[str, Any] = {}
    for key, value in schema.members.items():
        if value.as_list:
            model.update(
                {
                    key: fields.Nested(
                        json_schema_to_flaskx(schema=value, namespace=namespace),
                        as_list=True,
                    )
                }
            )
        else:
            model.update(
                {key: json_schema_to_flaskx(schema=value, namespace=namespace)}
            )
    if schema.schema_name:
        return _register_model_for_documentation(schema.schema_name, namespace, model)
    return model


def json_schema_to_flaskx(
    schema: JsonValue, namespace: Namespace
) -> Union[
    Model,
    Dict[str, Any],
    type[fields.String],
    type[fields.Arbitrary],
    type[fields.Boolean],
    type[fields.DateTime],
]:
    if isinstance(schema, JsonDict):
        model = _convert_json_dict(schema, namespace)
        return model
    elif isinstance(schema, JsonDecimal):
        return fields.Arbitrary
    elif isinstance(schema, JsonBoolean):
        return fields.Boolean
    elif isinstance(schema, JsonDatetime):
        return fields.DateTime
    else:
        assert isinstance(schema, JsonString)
        return fields.String
