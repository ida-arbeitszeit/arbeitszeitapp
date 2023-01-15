from typing import Any, Dict, Union

from flask_restx import Model, Namespace, fields

from arbeitszeit_web.api_presenters.interfaces import JsonDict, JsonString, JsonValue


def register(schema: JsonDict, namespace: Namespace) -> Model:
    assert schema.schema_name
    model = {
        key: json_schema_to_flaskx(schema=value, namespace=namespace)
        for key, value in schema.members.items()
    }
    result = namespace.model(name=schema.schema_name, model=model)
    return result


def register_as_nested(schema: JsonDict, namespace: Namespace) -> Model:
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
            if schema.as_list:
                model = register_as_nested(schema, namespace)
                return model
            else:
                model = register(schema, namespace)
                return model
    elif isinstance(schema, JsonString):
        return fields.String
    else:
        raise ValueError()
