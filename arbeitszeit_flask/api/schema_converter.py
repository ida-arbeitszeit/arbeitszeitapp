from typing import TypeAlias, Union

from deepdiff import DeepDiff
from flask_restx import Model, fields

from arbeitszeit_web.api.presenters.interfaces import (
    JsonBoolean,
    JsonDatetime,
    JsonDecimal,
    JsonInteger,
    JsonList,
    JsonObject,
    JsonString,
    JsonValue,
    Namespace,
)

RestxField: TypeAlias = Union[
    fields.List,
    fields.Nested,
    fields.String,
    fields.Arbitrary,
    fields.Boolean,
    fields.DateTime,
    fields.Integer,
    fields.List,
    dict[str, "RestxField"],
]


class DifferentModelWithSameNameExists(Exception):
    pass


class SchemaConverter:
    def __init__(self, namespace: Namespace) -> None:
        self.namespace = namespace

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

    def json_schema_to_flaskx(self, schema: JsonValue) -> Union[Model, RestxField]:
        if isinstance(schema, JsonObject):
            model = Model(schema.name, self.field_from_schema(schema))
            self._prevent_overriding(model)
            self.namespace.model(name=model.name, model=model)
            return model
        else:
            return self.field_from_schema(schema)

    def field_from_schema(self, schema: JsonValue) -> RestxField:
        match schema:
            case JsonObject(members=members):
                return {
                    key: self.field_from_schema(value) for key, value in members.items()
                }
            case JsonList(elements=JsonObject() as elements, required=required):
                object_model = Model(
                    elements.name,
                    self.field_from_schema(elements),
                )
                self._prevent_overriding(object_model)
                self.namespace.model(name=elements.name, model=object_model)
                return fields.List(
                    fields.Nested(object_model, skip_none=True), required=required
                )
            case JsonString(required=required):
                return fields.String(required=required)
            case JsonDecimal(required=required):
                return fields.Arbitrary(required=required)
            case JsonBoolean(required=required):
                return fields.Boolean(required=required)
            case JsonInteger(required=required):
                return fields.Integer(required=required)
            case JsonDatetime(required=required):
                return fields.DateTime(required=required)
            case other:
                raise NotImplementedError(other)
