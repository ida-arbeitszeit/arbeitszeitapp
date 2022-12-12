from typing import Dict, Protocol


class Model(Protocol):
    ...


class Namespace(Protocol):
    def marshal_with(self, model: Model):
        ...

    def model(self, name: str, model: Dict) -> Model:
        ...
