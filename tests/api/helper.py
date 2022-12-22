from dataclasses import asdict
from typing import Any, Callable, Dict

from arbeitszeit_web.api_presenters.interfaces import Decimal, Model, Nested, String


class StringImpl:
    ...


class DecimalImpl:
    ...


class NestedImpl:
    def __init__(self, model: Model, as_list: bool = False) -> None:
        self.model = model
        self.as_list = as_list


class FieldTypes:
    def __init__(self) -> None:
        self.string: type[String] = StringImpl
        self.decimal: type[Decimal] = DecimalImpl
        self.nested: type[Nested] = NestedImpl


class ModelImpl:
    ...


class NamespaceImpl:
    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
        self.models: Dict[str, Model] = {}

    def add_resource(self, resource, *urls, **kwargs):
        ...

    def route(self, *urls, **kwargs):
        ...

    def add_model(self, name: str, definition: Model) -> Model:
        self.models[name] = definition
        return definition

    def model(self, name: str, model: Dict[str, Any]) -> Model:
        return self.add_model(name, model)

    def _obj_to_dictionary(self, use_case_response: Any) -> Dict:
        return asdict(use_case_response)

    def marshal_with(self, model: Model):
        """This test implementation only sets an attribute to true."""

        def wrapper(func: Callable):
            response = func()
            response.has_been_marshalled = True
            return response

        return wrapper
