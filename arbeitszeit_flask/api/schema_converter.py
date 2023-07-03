from typing import Any, Dict, Union

from deepdiff import DeepDiff
from flask_restx import Model, fields

from arbeitszeit_web.api.presenters.interfaces import (
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

    def _register_on_namespace(self, flaskx_model: Model) -> None:
        self.namespace.model(name=flaskx_model.name, model=flaskx_model)

    def _prevent_overriding(self, model: Model) -> None:
        """
        Ensure that a model previously registered on namespace does not get overridden by a different one that has the same name.
        """
        if model.name in self.namespace.models:
            if not DeepDiff(self.namespace.models[model.name], model):
                pass
            else:
                raise DifferentModelWithSameNameExists(
                    f"Different model with name {model.name} exists already."
                )

    def _dict_to_flaskx_model(
        self, model_name: str, dict_model: Dict[str, Any]
    ) -> Model:
        flaskx_model = Model(name=model_name)
        flaskx_model.update(dict_model)
        return flaskx_model

    def _unpack_member_in_list(
        self, dict_model: Dict[str, Any], key: str, json_value: JsonValue
    ) -> Dict[str, Any]:
        if isinstance(json_value, JsonObject):
            dict_model.update(
                {
                    key: fields.List(
                        fields.Nested(
                            self.json_schema_to_flaskx(schema=json_value),
                            skip_none=True,
                        ),
                        required=True,
                    )
                }
            )
        else:
            dict_model.update(
                {
                    key: fields.List(
                        self.json_schema_to_flaskx(schema=json_value), required=True
                    )
                }
            )
        return dict_model

    def _unpack_object_members_recursively(
        self, json_object: JsonObject
    ) -> Dict[str, Any]:
        dict_model: Dict[str, Any] = {}
        for key, json_value in json_object.members.items():
            if json_value.as_list:
                dict_model = self._unpack_member_in_list(dict_model, key, json_value)
            else:
                dict_model.update({key: self.json_schema_to_flaskx(schema=json_value)})
        return dict_model

    def json_schema_to_flaskx(
        self, schema: JsonValue
    ) -> Union[
        Model,
        fields.String,
        fields.Arbitrary,
        fields.Boolean,
        fields.DateTime,
        fields.Integer,
    ]:
        if isinstance(schema, JsonObject):
            dict_model = self._unpack_object_members_recursively(schema)
            flaskx_model = self._dict_to_flaskx_model(
                model_name=schema.name, dict_model=dict_model
            )
            self._prevent_overriding(flaskx_model)
            self._register_on_namespace(flaskx_model)
            return flaskx_model
        elif isinstance(schema, JsonDecimal):
            return fields.Arbitrary(required=schema.required)
        elif isinstance(schema, JsonBoolean):
            return fields.Boolean(required=schema.required)
        elif isinstance(schema, JsonDatetime):
            return fields.DateTime(required=schema.required)
        elif isinstance(schema, JsonInteger):
            return fields.Integer(required=schema.required)
        else:
            assert isinstance(schema, JsonString)
            return fields.String(required=schema.required)
