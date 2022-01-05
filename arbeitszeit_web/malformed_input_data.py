from dataclasses import dataclass


@dataclass(frozen=True)
class MalformedInputData:
    field: str
    message: str
