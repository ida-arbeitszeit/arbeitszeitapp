from typing import TypeAlias, Union

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
        self._registered_schemas = RegisteredSchemas(namespace)

    def json_schema_to_flaskx(self, schema: JsonValue) -> Union[Model, RestxField]:
        if isinstance(schema, JsonObject):
            self._prevent_overriding(schema)
            self._registered_schemas[schema.name] = schema
            model = Model(schema.name, self._field_from_schema(schema))
            self.namespace.model(name=model.name, model=model)
            return model
        else:
            return self._field_from_schema(schema)

    def _prevent_overriding(self, schema: JsonObject) -> None:
        """
        Ensure that a model previously registered on namespace does not
        get overridden by a different one that has the same name.
        """
        try:
            registered_schema = self._registered_schemas[schema.name]
        except KeyError:
            return
        if registered_schema is not schema:
            raise DifferentModelWithSameNameExists(
                f"Different model with name '{schema.name}' exists already."
            )

    def _field_from_schema(self, schema: JsonValue) -> RestxField:
        match schema:
            case JsonObject(members=members):
                return {
                    key: self._field_from_schema(value)
                    for key, value in members.items()
                }
            case JsonList(elements=JsonObject() as elements, required=required):
                object_model = Model(
                    elements.name,
                    self._field_from_schema(elements),
                )
                self._prevent_overriding(elements)
                self._registered_schemas[elements.name] = elements
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


class RegisteredSchemas:
    def __init__(self, namespace: Namespace) -> None:
        self._namespace = namespace
        # We need to store the data about already registered models with the
        # namespace since this is our source of truth.
        self._namespace.schemas = dict()  # type: ignore

    def __setitem__(self, name: str, value: JsonValue) -> None:
        self._namespace.schemas[name] = value  # type: ignore

    def __getitem__(self, name: str) -> JsonValue:
        return self._namespace.schemas[name]  # type: ignore
