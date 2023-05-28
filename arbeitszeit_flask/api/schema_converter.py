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


class SchemaConverter:
    def __init__(self, namespace: Namespace) -> None:
        self.namespace = namespace

    def _prevent_overriding(self, schema_name: str, model: Dict[str, Any]) -> None:
        """
        Ensure that a model previously registered on namespace does not get overridden by a different one that has the same name.
        """
        if schema_name in self.namespace.models:
            if self.namespace.models[schema_name] == model:
                pass
            else:
                raise DifferentModelWithSameNameExists(
                    f"Different model with name {schema_name} exists already."
                )

    def _register_model(self, model_name: str, raw_model: Dict[str, Any]) -> Model:
        self._prevent_overriding(model_name, raw_model)
        registered_model = self.namespace.model(name=model_name, model=raw_model)
        return registered_model

    def _unpack_member_in_list(
        self, raw_model: Dict[str, Any], key: str, json_value: JsonValue
    ) -> Dict[str, Any]:
        if isinstance(json_value, JsonObject):
            raw_model.update(
                {
                    key: fields.List(
                        fields.Nested(
                            self.json_schema_to_flaskx(schema=json_value),
                        )
                    )
                }
            )
        else:
            raw_model.update(
                {key: fields.List(self.json_schema_to_flaskx(schema=json_value))}
            )
        return raw_model

    def _unpack_object_members_recursively(
        self, json_object: JsonObject
    ) -> Dict[str, Any]:
        raw_model: Dict[str, Any] = {}
        for key, json_value in json_object.members.items():
            if json_value.as_list:
                raw_model = self._unpack_member_in_list(raw_model, key, json_value)
            else:
                raw_model.update({key: self.json_schema_to_flaskx(schema=json_value)})
        return raw_model

    def _convert_and_register_json_object(self, json_object: JsonObject) -> Model:
        raw_model = self._unpack_object_members_recursively(json_object)
        registered_model = self._register_model(
            model_name=json_object.name, raw_model=raw_model
        )
        return registered_model

    def json_schema_to_flaskx(
        self, schema: JsonValue
    ) -> Union[
        Model,
        type[fields.String],
        type[fields.Arbitrary],
        type[fields.Boolean],
        type[fields.DateTime],
        type[fields.Integer],
    ]:
        if isinstance(schema, JsonObject):
            model = self._convert_and_register_json_object(schema)
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
