from typing import Dict, Protocol


class ModelImpl:
    def __init__(self, name: str, model: Dict) -> None:
        self.name = name
        self.model = model


class NamespaceImpl:
    def marshal_with(self, model: ModelImpl):
        def wrapper(func):
            return model

        return wrapper

    def model(self, name: str, model: Dict) -> ModelImpl:
        return ModelImpl(name=name, model=model)
