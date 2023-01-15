from typing import Any, Dict


class NamespaceImpl:
    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
        self.models: Dict[str, Any] = {}

    def model(self, name: str, model: Any) -> Any:
        self.models[name] = model
        return model
