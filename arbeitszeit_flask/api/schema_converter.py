from typing import Any, Dict, Union

from flask_restx import Model, fields

from arbeitszeit_web.api_presenters.interfaces import (
    JsonBoolean,
    JsonDatetime,
    JsonDecimal,
    JsonInteger,
    JsonObject,
    JsonString,
    JsonValue,
    Namespace,
)


class DifferentModelWithSameNameExists(Exception):
    pass


def _prevent_overriding(
    schema_name: str, namespace: Namespace, model: Dict[str, Any]
) -> None:
    """
    Ensure that a model previously registered on namespace does not get overridden by a different one that has the same name.
    """
    if schema_name in namespace.models:
        if namespace.models[schema_name] == model:
            pass
        else:
            raise DifferentModelWithSameNameExists(
                f"Different model with name {schema_name} exists already."
            )


def _register_model(
    model_name: str, namespace: Namespace, raw_model: Dict[str, Any]
) -> Model:
    _prevent_overriding(model_name, namespace, raw_model)
    registered_model = namespace.model(name=model_name, model=raw_model)
    return registered_model


def _convert_json_object_to_restx_model(
    json_object: JsonObject, namespace: Namespace
) -> Model:
    raw_model: Dict[str, Any] = {}
    for key, json_value in json_object.members.items():
        if json_value.as_list:
            if isinstance(json_value, JsonObject):
                raw_model.update(
                    {
                        key: fields.List(
                            fields.Nested(
                                json_schema_to_flaskx(
                                    schema=json_value, namespace=namespace
                                ),
                            )
                        )
                    }
                )
            else:
                raw_model.update(
                    {
                        key: fields.List(
                            json_schema_to_flaskx(
                                schema=json_value, namespace=namespace
                            )
                        )
                    }
                )
        else:
            raw_model.update(
                {key: json_schema_to_flaskx(schema=json_value, namespace=namespace)}
            )
    registered_model = _register_model(
        model_name=json_object.name, namespace=namespace, raw_model=raw_model
    )
    return registered_model


def json_schema_to_flaskx(
    schema: JsonValue, namespace: Namespace
) -> Union[
    Model,
    type[fields.String],
    type[fields.Arbitrary],
    type[fields.Boolean],
    type[fields.DateTime],
    type[fields.Integer],
]:
    if isinstance(schema, JsonObject):
        model = _convert_json_object_to_restx_model(schema, namespace)
        return model
    elif isinstance(schema, JsonDecimal):
        return fields.Arbitrary
    elif isinstance(schema, JsonBoolean):
        return fields.Boolean
    elif isinstance(schema, JsonDatetime):
        return fields.DateTime
    elif isinstance(schema, JsonInteger):
        return fields.Integer
    else:
        assert isinstance(schema, JsonString)
        return fields.String
