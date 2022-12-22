from typing import Any, Dict, Protocol


class String(Protocol):
    ...


class Decimal(Protocol):
    ...


class Nested(Protocol):
    """
    Allows you to nest one set of fields inside another.
    """

    def __init__(self, model: "Model", as_list: bool = False) -> None:
        ...


class FieldTypes(Protocol):
    string: type[String]
    decimal: type[Decimal]
    nested: type[Nested]


class Model(Protocol):
    @property
    def keys(self):
        ...


class Namespace(Protocol):
    """
    Group resources together.
    """

    def __init__(self, name: str, description: str) -> None:
        ...

    def add_resource(self, resource, *urls, **kwargs):
        """
        Register a Resource for a given API Namespace
        """
        ...

    def route(self, *urls, **kwargs):
        """
        A decorator to route resources.
        """
        ...

    def add_model(self, name: str, definition: Model) -> Model:
        ...

    def model(self, name: str, model: Dict[str, Any]) -> Model:
        """
        Register a model
        """
        ...

    def marshal_with(self, model: Model):
        ...
